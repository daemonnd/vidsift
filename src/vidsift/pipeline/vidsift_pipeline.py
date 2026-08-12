"""
Vidsifts orchestrator
It gets called by main.py

The ONLY top-level orchestrator

What it does:
- define pipeline stages
- control ordering
- pass structured data between steps
- handle reties/failure strategy
"""

import logging
from collections.abc import Callable
from pathlib import Path
from sys import exit
from typing import Generator, Literal

from vidsift.config.models import AppConfig, ChannelConfig
from vidsift.features.download.downloader import VideoDownloader
from vidsift.features.transcript.errors import TranscriptError
from vidsift.features.validation.errors import VideoValidationError
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.ingestion.errors import (IngestionEnrichmentError,
                                      VideoDataCollectionError,
                                      VideoFilteringError)
from vidsift.ingestion.video_filter import VideoFilter
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import InvalidVideoError, Video
from vidsift.models.video_record import (VideoProcessingRecord,
                                         VideoProcessingStatus)
from vidsift.services.summarization_service import SummarizationService
from vidsift.services.transcript_service import TranscriptService
from vidsift.services.validation_service import VideoValidator
from vidsift.services.video_data_collection_service import VideoDataCollection
from vidsift.shared.channel_lookup import get_channel_lookup
from vidsift.shared.delay_calculator import calculate_delay, sleep_delay
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.video_discovery_source import DiscoverySource

logger = logging.getLogger(__name__)


class VidsiftOrchestrator:
    def __init__(
        self,
        config: AppConfig,
        video_validator: VideoValidator | None = None,
        transcript_service: TranscriptService | None = None,
        summarizer: SummarizationService | None = None,
        downloader: VideoDownloader | None = None,
        video_db: VideoProcessingRepository | None = None,
        video_filter: VideoFilter | None = None,
        should_sleep: bool = True,
    ):
        self.config: AppConfig = config

        channel_id_list: list[str] = []
        for channel in config.channels:
            channel_id_list.append(channel.id)
        # video fetching
        self.video_data_collector: VideoDataCollection = VideoDataCollection(
            channel_id_list=channel_id_list, config=config
        )
        # video filtering
        self.video_filter: VideoFilter = video_filter or VideoFilter(config=config)
        # video cache
        self.video_db: VideoProcessingRepository = (
            video_db or VideoProcessingRepository(config=self.config)
        )
        # validation
        self.video_validator: VideoValidator = video_validator or VideoValidator(config)
        # transcript
        self.transcript_service: TranscriptService = (
            transcript_service or TranscriptService(config)
        )
        # summarization
        self.summarizer: SummarizationService = summarizer or SummarizationService(
            config
        )
        # downloading
        self.downloader: VideoDownloader = downloader or VideoDownloader(config=config)

        # delay
        self.should_sleep: bool = should_sleep

    def run(
        self,
        skip_interrupted_vids: bool | None = None,
        skip_new_vids: bool | None = None,
    ) -> None:
        if skip_interrupted_vids is None:
            skip_interrupted_vids = self.config.video_processing.skip_interrupted_vids
        if skip_new_vids is None:
            skip_new_vids = self.config.video_processing.skip_new_vids

        if skip_interrupted_vids and skip_new_vids:
            logger.info(
                "No videos will be processed because both interrupted video processing and new video processing are disabled",
                extra={"event": LogEvent.NO_VIDEO_GETS_PROCESSED},
            )
            return
        try:
            self.video_db.open()
            logger.info(
                "The vidsift orchestrator started.",
                extra={"event": LogEvent.ORCHESTRATOR_STARTED},
            )

            if not skip_interrupted_vids:
                # before fetching and processing any new videos, process the interrupted / failed ones
                self.process_interrupted_videos()

            # new videos
            if not skip_new_vids:
                try:
                    video_generator: Generator[
                        tuple[Video, DiscoverySource], None, None
                    ] = self.video_data_collector.get_videos_to_process()
                except VideoDataCollectionError as e:
                    logger.exception(
                        f"VideoDataCollectionError: Failed to collect the necessary data about the videos to process: {str(e)}",
                        extra={
                            "event": LogEvent.RSS_FETCH_FAILED,
                        },
                    )
                    logger.info("Exiting because no data exist...")
                    exit(1)

                # process new videos
                channel_lookup = get_channel_lookup(self.config.channels)
                for vid, discovery_type in video_generator:
                    # if the video is already in the db, it does not get processed
                    if self.video_db.exists(video_id=vid.video_id):
                        logger.debug(
                            f"Skipping video with video id '{vid.video_id}' because it was already processed.",
                            extra={
                                "event": LogEvent.VIDEO_SKIPPED_EXISTING,
                                "video_id": vid.video_id,
                                "channel_id": vid.channel_id,
                            },
                        )
                        continue  # no delay waiting
                    # check if the video is a livestream or member-only content
                    # does not do the filtering for fallback (assumed that it is only videos)
                    self.video_db.create(
                        vid=vid
                    )  # put the data about the video into the db, with status FILTERING
                    if discovery_type == DiscoverySource.RSS:
                        processing: bool = self._enrich_and_filter_video(vid=vid, discovery_type=discovery_type, channel_lookup=channel_lookup)
                        if not processing:
                            continue
                    logger.debug(
                        f"Processing video with video id '{vid.video_id}' because it passed the filters",
                        extra={
                            "event": LogEvent.VIDEO_FILTERING_COMPLETED,
                            "passed": True,
                            "discovery_source": discovery_type.value,
                            "video_id": vid.video_id,
                            "channel_id": vid.channel_id,
                        },
                    )
                    self.process_video(vid=vid, channel_lookup=channel_lookup)
        finally:
            self.video_db.close()
            logger.info(
                "The vidsift orchestrator has been stopped.",
                extra={
                    "event": LogEvent.ORCHESTRATOR_STOPPED,
                },
            )

    def _enrich_and_filter_video(
        self,
        vid: Video,
        discovery_type: DiscoverySource,
        channel_lookup: dict[str, ChannelConfig]
    ) -> bool:
        """
        Method that enriches the video data and runs the filtering on it 
        because filtering requires data enrichment, the filtering is done after the enrichment.
        Returns:
            - True if it passed all of the filters
            - False if it failed on one filter
        """
        # extract additional video data
        try:
            enrichment_data: dict = self.video_data_collector.get_additional_video_data(vid=vid)
        except IngestionEnrichmentError as e:
            logger.exception(
                f"Failed to fetch additional video data for video '{vid.video_id}': {str(e)}",
                extra={"event": LogEvent.VIDEO_METADATA_ENRICHMENT_FAILED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id
                },
            )
            processing: bool = self.should_process(vid, discovery_type, channel_lookup, error_message=str(e))
        except BaseException:
            raise
        else:
            self.video_db.del_row(video_id=vid.video_id)  # delete the row, because it will be re-created with the enriched data
            self.video_db.create(vid=Video.apply_duration_enrichment(video=vid, duration=enrichment_data.get("duration")))  # re-create the row with the enriched data
            processing: bool = self.should_process(
                vid=vid,
                discovery_type=discovery_type,
                channel_lookup=channel_lookup,
                data=enrichment_data,
            )
        return processing
    def process_video(self, vid: Video, channel_lookup: dict[str, ChannelConfig]):
        channel = channel_lookup[vid.channel_id]
        match channel.action:
            case "download":
                logger.info(
                    f"Processing video with video id '{vid.video_id}' from {vid.author} with action download",
                    extra={
                        "event": LogEvent.VIDEO_DOWNLOAD_STARTED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                    },
                )
                self.execute_processing_step(
                    vid=vid,
                    step_type="download",
                    success_decision="downloaded",
                    starting_status=VideoProcessingStatus.DOWNLOADING,
                    action=lambda: self.downloader.download(
                        video_url=vid.url,
                        output_path=Path(self.config.downloads.output_dir),
                    ),
                )
            case "summarize":
                logger.info(
                    f"Processing video with video id '{vid.video_id}' from {vid.author} with action summarize",
                    extra={
                        "event": LogEvent.VIDEO_SUMMARIZATION_STARTED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                    },
                )
                transcript = self.manage_transcript_fetch(vid=vid)
                if transcript is None:
                    return
                self.execute_processing_step(
                    vid=vid,
                    step_type="summarize",
                    starting_status=VideoProcessingStatus.SUMMARIZING,
                    success_decision="summarized",
                    action=lambda: self.summarizer.summarize(
                        raw_transcript=transcript, vid=vid
                    ),
                )
            case "validate":
                logger.info(
                    f"Processing video with video id '{vid.video_id}' from {vid.author} with action validate",
                    extra={
                        "event": LogEvent.VIDEO_VALIDATION_STARTED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                    },
                )
                self.process_validation_pipeline(vid=vid, create_db_entry=False)

    def _filter_video_out(
        self,
        vid: Video,
        reason: Literal["livestream", "members-only"],
        channel_lookup: dict[str, ChannelConfig],
        exception: bool
    ):
        match reason:
            case "livestream":
                logger.info(
                    f"Skipped video with video id '{vid.video_id}' with title '{vid.title}' because it is a livestream."
                    if not exception else
                    f"Skipped video with video id '{vid.video_id}' with title '{vid.title}' because it is probably a livestream.",
                    extra={
                        "event": LogEvent.VIDEO_FILTERING_COMPLETED,
                        "passed": False,
                        "error_msg_parsed": str(exception),
                        "reason": "livestream",
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                    },
                )
            case "members-only":
                logger.info(
                    f"Skipped video with video id '{vid.video_id}' with title '{vid.title}' because it is members-only content"
                    if not exception else
                    f"Skipped video with video id '{vid.video_id}' with title '{vid.title}' because it is probably members-only content",
                    extra={
                        "event": LogEvent.VIDEO_FILTERING_COMPLETED,
                        "passed": False,
                        "error_msg_parsed": str(exception),
                        "reason": "members-only",
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                    }
                )

        self.video_db.set_status(
            video_id=vid.video_id, status=VideoProcessingStatus.DONE
        )
        if channel_lookup[vid.channel_id].action == "validate":
            self.video_db.save_validation_result(
                video_id=vid.video_id,
                decision="discarded",
                quality_score=0.0,
                topic_match_score=0.0,
                reason="Filterd out because it is a livestream." if reason == "livestream" else "Filtered out because it is members-only content",
            )
            self.video_db.update_after_done(
                video_id=vid.video_id, decision="discarded"
            )
    def should_process(
        self,
        vid: Video,
        discovery_type: DiscoverySource,
        channel_lookup: dict[str, ChannelConfig],
        data: dict | None = None,
        error_message: str | None = None
    ) -> bool:
        """
        Method to manage video filtering
        Return:
            - `True` if it passed all of the filters
            - `False` if it failed on one filter
        """
        # not set the status to filtering, because it is requires data enrichment, and not all data from data enrichment is stored
 
        try:
            logger.debug(
                f"Checking wether video with video id '{vid.video_id}' should be processed",
                extra={
                    "event": LogEvent.VIDEO_FILTERING_STARTED,
                    "discovery_source": discovery_type.value,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            passes, reason = self.video_filter.run_filters(vid=vid, data=data, error_message=error_message)
        except (
            VideoFilteringError
        ) as e:
            # on other error
            logger.exception(
                f"VideoFilteringError: Failed to filter video '{vid.video_id}': {str(e)}",
                extra={
                    "event": LogEvent.VIDEO_FILTERING_FAILED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            self.video_db.mark_failed(
                error_msg=repr(e),
                video_id=vid.video_id,
                target_status=VideoProcessingStatus.DATA_ENRICHING # filtering requires data enrichment, so the status is set to data enriching, so that it can be re-processed
            )
            return False
        except BaseException:
            raise
        else:
            if passes is False:
                self._filter_video_out(vid=vid, reason=reason, channel_lookup=channel_lookup, exception=False)
                return False
            return True

    def execute_processing_step(
        self,
        vid: Video,
        step_type: Literal["download", "summarize"],
        success_decision: Literal["downloaded", "summarized"],
        starting_status: VideoProcessingStatus,
        action: Callable[[], None],
    ) -> bool:
        """
        Video execution wrapper.
        Executes downloader and summarizer.
        Responsabilities:
        - set status
        - excute action
        - handle + log start, completed and failure

        Returns true if it succeeded, false if it failed
        """

        starting_event, completed_event, failure_event = (
            LogEvent.get_final_output_events(general_event=step_type)
        )

        self.video_db.set_status(video_id=vid.video_id, status=starting_status)

        logger.info(
            f"Starting video {step_type}.",
            extra={
                "event": starting_event,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )

        try:
            action()
        except InvalidVideoError:
            raise
        except Exception as e:
            logger.exception(
                f"{type(e).__name__}: Failed to {step_type} video with id {vid.video_id}: {str(e)}",
                extra={
                    "event": failure_event,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            self.video_db.mark_failed(error_msg=repr(e), video_id=vid.video_id)
            return False
        except BaseException:
            raise
        else:
            self.video_db.update_after_done(
                video_id=vid.video_id, decision=success_decision
            )
            logger.info(
                f"Video {step_type} completed.",
                extra={
                    "event": completed_event,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            return True

    def take_action_on_video(
        self, video_validation_result: ValidationResult, transcript: str, vid: Video
    ):
        # take the appropriate action based on the validation result
        match video_validation_result.decision:
            case "downloaded":
                self.execute_processing_step(
                    vid=vid,
                    step_type="download",
                    success_decision="downloaded",
                    starting_status=VideoProcessingStatus.DOWNLOADING,
                    action=lambda: self.downloader.download(
                        video_url=vid.url,
                        output_path=Path(self.config.downloads.output_dir),
                    ),
                )
            case "summarized":
                self.execute_processing_step(
                    vid=vid,
                    step_type="summarize",
                    success_decision="summarized",
                    starting_status=VideoProcessingStatus.SUMMARIZING,
                    action=lambda: self.summarizer.summarize(
                        raw_transcript=transcript, vid=vid
                    ),
                )
            case "discarded":
                # add it to the video cache
                self.video_db.update_after_done(
                    video_id=vid.video_id, decision="discarded"
                )

    def fetch_transcript(self, vid: Video) -> str:
        # fetch the transcript
        logger.debug(
            f"Fetching the transcript of {vid.video_id}...",
            extra={
                "event": LogEvent.TRANSCRIPT_FETCH_STARTED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )
        transcript: str = self.transcript_service.get_transcript(vid)
        logger.debug(
            f"Finished fetching the transcript of {vid.video_id}",
            extra={
                "event": LogEvent.TRANSCRIPT_FETCH_COMPLETED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )
        return transcript

    def manage_transcript_fetch(self, vid: Video) -> str | None:
        """
        Method that manages the entire transcript fetching process, logs errors and creates db entries.
        Returns None on failure, the transcript as a string on success
        """
        try:
            # fetch the transcript
            logger.debug(
                f"Fetching the transcript of {vid.video_id}...",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_STARTED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            transcript: str = self.transcript_service.get_transcript(vid)
            logger.debug(
                f"Finished fetching the transcript of {vid.video_id}",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_COMPLETED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
        except TranscriptError as e:
            error_msg: str = (
                f"TranscriptError: Each transcript fetching provider failed: {str(e)}"
            )
            logger.exception(
                error_msg,
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            # add the failure to the video database
            self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
            logger.info(
                "Moving on to the next video because of the previous TranscriptError..."
            )
            self.cooldown()
            return
        else:
            return transcript

    def resume_downloads(self):
        # download the videos with an interrupted download
        logger.debug(
            "Check for videos where the download got interrupted...",
            extra={"event": LogEvent.DOWNLOAD_RESUME_STARTED},
        )
        downloading_vids_generator: Generator[VideoProcessingRecord, None, None] = (
            self.video_db.get_by_status("downloading")
        )
        for video in downloading_vids_generator:
            try:
                vid: Video = Video.from_cache(video_db_row=video)
            except InvalidVideoError:
                raise
            logger.info(
                f"Processing video {vid.video_id} that got interrupted while downloading.",
                extra={
                    "event": LogEvent.PROCESSING_DOWNLOAD_RESUME,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            self.execute_processing_step(
                vid=vid,
                success_decision="downloaded",
                starting_status=VideoProcessingStatus.DOWNLOADING,
                step_type="download",
                action=lambda: self.downloader.download(
                    video_url=vid.url,
                    output_path=Path(self.config.downloads.output_dir),
                ),
            )
            self.cooldown()
        logger.debug(
            "Check for videos where the download got interrupted... Done",
            extra={
                "event": LogEvent.DOWNLOAD_RESUME_COMPLETED,
            },
        )

    def resume_data_enriching(self):
        # resume data enriching that got interrupted (due to an error)
        logger.debug(
            "Check for videos that got interrupted while enriching their metadata...",
            extra={"event": LogEvent.VIDEO_METADATA_ENRICHMENT_RESUME_STARTED},
        )
        filtering_videos: Generator[VideoProcessingRecord, None, None] = (
            self.video_db.get_by_status("data_enriching")
        )
        channel_lookup = get_channel_lookup(self.config.channels)
        for video in filtering_videos:
            vid: Video = Video.from_cache(video_db_row=video)
            logger.info(
                f"Processing video with video id '{vid.video_id}' that got interrupted while enriching its metadata.",
                extra={
                    "event": LogEvent.PROCESSING_VIDEO_METADATA_ENRICHMENT_RESUME,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            if self.should_process(
                vid=vid,
                discovery_type=DiscoverySource.RSS,  # has to be rss, else the video would not end up in livestream checking state, it would immediately get processed,
                channel_lookup=channel_lookup,
            ):
                self.process_video(vid=vid, channel_lookup=channel_lookup)
        logger.debug(
            "Check for videos where filtering got interrupted... Done",
            extra={
                "event": LogEvent.VIDEO_METADATA_ENRICHMENT_RESUME_COMPLETED,
            },
        )

    def resume_validations(self):
        # re-validate the videos where only the metadata is present
        logger.debug(
            "Check for videos where the validation got interrupted...",
            extra={"event": LogEvent.VALIDATION_RESUME_STARTED},
        )
        validating_vids_generator: Generator[VideoProcessingRecord, None, None] = (
            self.video_db.get_by_status("validating")
        )
        for video in validating_vids_generator:
            vid: Video = Video.from_cache(video_db_row=video)
            logger.info(
                f"Processing video {vid.video_id} that got interrupted while validating.",
                extra={
                    "event": LogEvent.PROCESSING_VALIDATION_RESUME,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            self.process_validation_pipeline(vid=vid, create_db_entry=False)
        logger.debug(
            "Check for videos where the validation got interrupted... Done",
            extra={
                "event": LogEvent.VALIDATION_RESUME_COMPLETED,
            },
        )

    def resume_summaries(self):
        # restart the summarization action for the videos where the summary got interrupted
        logger.debug(
            "Check for videos where the summarization got interrupted...",
            extra={"event": LogEvent.SUMMARIZATION_RESUME_STARTED},
        )
        summarizing_vids_generator: Generator[VideoProcessingRecord, None, None] = (
            self.video_db.get_by_status("summarizing")
        )
        for video in summarizing_vids_generator:
            vid: Video = Video.from_cache(video_db_row=video)
            logger.info(
                f"Processing video {vid.video_id} that got interrupted while summarizing.",
                extra={
                    "event": LogEvent.PROCESSING_SUMMARIZATION_RESUME,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            try:
                transcript = self.manage_transcript_fetch(vid=vid)
                if transcript is None:
                    continue
                if not self.execute_processing_step(
                    vid=vid,
                    step_type="summarize",
                    success_decision="summarized",
                    starting_status=VideoProcessingStatus.SUMMARIZING,
                    action=lambda: self.summarizer.summarize(
                        raw_transcript=transcript, vid=vid
                    ),
                ):
                    continue
            except SystemExit, KeyboardInterrupt:
                self.should_sleep = False
                raise  # raise it to main, so that vidsift can exit
            finally:
                self.cooldown()
        logger.debug(
            "Check for videos where the summarization got interrupted... Done",
            extra={
                "event": LogEvent.SUMMARIZATION_RESUME_COMPLETED,
            },
        )

    def process_validation_pipeline(self, vid: Video, create_db_entry: bool):
        if create_db_entry:
            # not process the video if a db entry exists but the video is new
            # check if the video has already been handled
            if self.video_db.exists(video_id=vid.video_id):
                logger.debug(
                    f"Skipping video with video id '{vid.video_id}' because it was already processed.",
                    extra={
                        "event": LogEvent.VIDEO_SKIPPED_EXISTING,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                    },
                )
                return  # no delay waiting

            # update the database, set the status to VALIDATING
            # only do that for new videos
            self.video_db.create(vid=vid)
            logger.debug(f"current status: {self.video_db.get(vid.video_id)}")
            logger.info(
                "Video processing started.",
                extra={
                    "event": LogEvent.VIDEO_PROCESSING_STARTED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )

        self.video_db.set_status(
            video_id=vid.video_id, status=VideoProcessingStatus.VALIDATING
        )
        transcript = self.manage_transcript_fetch(vid=vid)
        if transcript is None:
            return
        # get the validation result
        logger.info(
            f"Starting validation for video {vid.video_id}.",
            extra={
                "event": LogEvent.VIDEO_VALIDATION_STARTED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )
        try:
            video_validation_result = self.video_validator.validate_video(
                vid=vid, raw_transcript=transcript
            )

        except VideoValidationError as e:
            # logs are handled by the validator, because the logs are more specific like this
            self.video_db.mark_failed(error_msg=repr(e), video_id=vid.video_id)
            return

        except InvalidVideoError:
            raise
        else:
            logger.info(
                f"Validation completed for video {vid.video_id} with decision '{video_validation_result.decision}'",
                extra={
                    "event": LogEvent.VIDEO_VALIDATION_COMPLETED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "decision": video_validation_result.decision,
                    "score": video_validation_result.content_quality_score,
                    "topic_match_score": video_validation_result.topic_match_score,
                    "reason": video_validation_result.summary_reason,
                },
            )

        # update the database after validation
        self.video_db.save_validation_result(
            video_id=vid.video_id,
            decision=video_validation_result.decision,
            quality_score=video_validation_result.content_quality_score,
            topic_match_score=video_validation_result.topic_match_score,
            reason=str(video_validation_result.summary_reason),
        )

        # take action on video based on the validation result
        self.take_action_on_video(
            vid=vid,
            video_validation_result=video_validation_result,
            transcript=transcript,
        )
        self.cooldown()

    def process_interrupted_videos(self):
        logger.info(
            "Starting to process interrupted videos",
            extra={"event": LogEvent.INTERRUPTED_PROCESSING_STARTED},
        )
        self.resume_data_enriching()
        self.resume_validations()
        self.resume_downloads()
        self.resume_summaries()
        logger.info(
            "Completed processing interrupted videos",
            extra={"event": LogEvent.INTERRUPTED_PROCESSING_COMPLETED},
        )

    def cooldown(self):
        sleep_delay(
            calculate_delay(
                min_delay=self.config.video_processing.min_vid_delay,
                random_delay=self.config.video_processing.random_vid_delay,
            ),
            should_sleep=self.should_sleep,
        )
