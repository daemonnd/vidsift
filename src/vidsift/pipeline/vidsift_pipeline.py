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

from vidsift.config.models import AppConfig
from vidsift.features.download.downloader import VideoDownloader
from vidsift.features.transcript.errors import TranscriptError
from vidsift.features.validation.errors import VideoValidationError
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.ingestion.errors import (VideoDataCollectionError,
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
        should_sleep: bool = True
    ):
        self.config: AppConfig = config

        channel_id_list: list[str] = []
        for channel in config.channels:
            channel_id_list.append(channel.id)
        # video fetching
        self.video_data_collector: VideoDataCollection = VideoDataCollection(channel_id_list=channel_id_list, config=config)
        # video filtering
        self.video_filter: VideoFilter = (video_filter or VideoFilter(config=config))
        # video cache
        self.video_db: VideoProcessingRepository = (video_db or VideoProcessingRepository(config=self.config))
        # validation
        self.video_validator: VideoValidator = (video_validator or VideoValidator(config))
        # transcript
        self.transcript_service: TranscriptService = (transcript_service or TranscriptService(config))
        # summarization
        self.summarizer: SummarizationService = (summarizer or SummarizationService(config))
        # downloading
        self.downloader: VideoDownloader = (downloader or VideoDownloader(config=config))

        # delay
        self.should_sleep: bool = should_sleep

    def run(self) -> None:
        try:
            self.video_db.open()
            logger.info(
                "The vidsift orchestrator started.",
                extra={"event": LogEvent.ORCHESTRATOR_STARTED},
            )

            # before fetching and processing any new videos, process the interrupted / failed ones
            self.process_interrupted_videos()

            # new videos
            try:
                logger.debug("RSS Fetch started",
                    extra={
                        "event": LogEvent.RSS_FETCH_STARTED,
                    }
                )
                video_generator: Generator[tuple[Video, DiscoverySource], None, None] = self.video_data_collector.get_videos_to_process()
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
                if self.video_db.exists(video_id=vid.video_id):
                    logger.debug(
                        f"Skipping video with video id {vid.video_id} because it was already processed.",
                        extra={
                            "event": LogEvent.VIDEO_SKIPPED_EXISTING,
                            "video_id": vid.video_id,
                            "channel_id": vid.channel_id,
                        },
                    )
                    continue # no delay waiting
                # check if the video is a livestream
                # does not do the livestream check for fallback (assumed that it is only videos)
                if discovery_type == DiscoverySource.RSS:
                    try:
                        logger.debug(
                            f"Cheching wether video with video id '{vid.video_id}' is a livestream",
                            extra={
                                "event": LogEvent.LIVESTREAM_CHECK_STARTED,
                                "discovery_source": discovery_type.value,
                                "video_id": vid.video_id,
                                "channel_id": vid.channel_id
                            }
                        )
                        is_livestream = self.video_filter.check_is_livestream(vid=vid)
                    except VideoFilteringError as e:
                        if "This live event will begin in" in str(e):
                            if str(e).endswith("minutes.") or str(e).endswith("hours.") or str(e).endswith("days."):
                                logger.info(
                                    f"Skipped video with video id {vid.video_id} with title '{vid.title}' because it is a livestream that will begin in the future",
                                    extra={
                                        "event": LogEvent.LIVESTREAM_CHECK_COMPLETED,
                                        "is_livestream": True,
                                        "video_id": vid.video_id,
                                        "channel_id": vid.channel_id
                                    }
                                )
                                self.video_db.create(vid=vid)
                                self.video_db.save_validation_result(
                                    video_id=vid.video_id,
                                    decision="discarded",
                                    quality_score=0.0,
                                    topic_match_score=0.0,
                                    reason="The video is a livestream that will begin in the future"
                                )
                                self.video_db.update_after_done(video_id=vid.video_id, decision="discarded")
                                continue
                        logger.exception(
                            f"VideoFilteringError: Failed to check if video is a livestream: {str(e)}",
                            extra={
                                "event": LogEvent.LIVESTREAM_CHECK_FAILED,
                                "video_id": vid.video_id,
                                "channel_id": vid.channel_id
                            }
                        )
                        self.video_db.create(vid=vid)
                        self.video_db.mark_failed(
                            error_msg=repr(e),
                            video_id=vid.video_id
                        )
                        continue
                    except Exception as e:
                        logger.exception(
                            f"Failed to check wether video with video id {vid.video_id} is a livestream: {str(e)}",
                            extra={
                                "event": LogEvent.LIVESTREAM_CHECK_FAILED,
                                "video_id": vid.video_id,
                                "channel_id": vid.channel_id
                            }
                        )
                        continue
                    except BaseException:
                        raise

                    if is_livestream:
                        logger.info(
                            f"Skipped video with video id {vid.video_id} with title {vid.title} because it is a livestream",
                            extra={
                                "event": LogEvent.LIVESTREAM_CHECK_COMPLETED,
                                "is_livestream": is_livestream,
                                "video_id": vid.video_id,
                                "channel_id": vid.channel_id
                            }
                        )
                        self.video_db.create(vid=vid)
                        self.video_db.save_validation_result(
                            video_id=vid.video_id,
                            decision="discarded",
                            quality_score=0.0,
                            topic_match_score=0.0,
                            reason="The video is a livestream"
                        )
                        self.video_db.update_after_done(video_id=vid.video_id, decision="discarded")
                        continue

                logger.debug(
                    f"Processing video with video id {vid.video_id} because it is not a livestream",
                    extra={
                        "event": LogEvent.LIVESTREAM_CHECK_COMPLETED,
                        "is_livestream": False,
                        "discovery_source": discovery_type.value,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id
                    }
                )
                self.video_db.create(vid=vid)

                channel = channel_lookup[vid.channel_id]
                match channel.action:
                    case "download":
                        logger.info(
                            f"Processing video with video id {vid.video_id} from {vid.author} with action download",
                            extra={
                                "event": LogEvent.VIDEO_DOWNLOAD_STARTED,
                                "video_id": vid.video_id,
                                "channel_id": vid.channel_id
                            }
                        )
                        self.execute_processing_step(
                            vid=vid,
                            step_type="download",
                            success_decision="downloaded",
                            starting_status=VideoProcessingStatus.DOWNLOADING,
                            action=lambda: self.downloader.download(
                                video_url=vid.url,
                                output_path=Path(self.config.downloads.output_dir)
                            )
                        )
                    case "summarize":
                        logger.info(
                            f"Processing video with video id {vid.video_id} from {vid.author} with action summarize",
                            extra={
                                "event": LogEvent.VIDEO_SUMMARIZATION_STARTED,
                                "video_id": vid.video_id,
                                "channel_id": vid.channel_id
                            }
                        )
                        try:
                            transcript: str = self.fetch_transcript(vid)
                        except TranscriptError as e:
                            error_msg: str = f"TranscriptError: Each transcript fetching provider failed: {str(e)}"
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
                            logger.info("Moving on to the next video because of the previous TranscriptError...")
                            sleep_delay(
                                calculate_delay(
                                    min_delay=self.config.video_processing.min_vid_delay,
                                    random_delay=self.config.video_processing.random_vid_delay
                                ),
                                should_sleep=self.should_sleep
                            )
                            continue
                        self.execute_processing_step(
                            vid=vid,
                            step_type="summarize",
                            starting_status=VideoProcessingStatus.SUMMARIZING,
                            success_decision="summarized",
                            action=lambda: self.summarizer.summarize(
                                raw_transcript=transcript,
                                vid=vid
                            )
                        )
                    case "validate":
                        logger.info(
                            f"Processing video with video id {vid.video_id} from {vid.author} with action validate",
                            extra={
                                "event": LogEvent.VIDEO_VALIDATION_STARTED,
                                "video_id": vid.video_id,
                                "channel_id": vid.channel_id
                            }
                        )
                        self.process_validation_pipeline(vid=vid, create_db_entry=False)

        finally:
            self.video_db.close()
            logger.info(
                "The vidsift orchestrator has been stopped.",
                extra={
                    "event": LogEvent.ORCHESTRATOR_STOPPED,
                },
            )

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

        starting_event, completed_event, failure_event = LogEvent.get_final_output_events(
            general_event=step_type
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
                    "channel_id": vid.channel_id
                }
            )
            self.video_db.mark_failed(
                error_msg=repr(e),
                video_id=vid.video_id
            )
            return False
        except BaseException:
            raise
        else:
            self.video_db.update_after_done(
                video_id=vid.video_id,
                decision=success_decision
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

    def take_action_on_video(self, video_validation_result: ValidationResult, transcript: str, vid: Video):
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
                        output_path=Path(self.config.downloads.output_dir)
                    )
                )
            case "summarized":
                self.execute_processing_step(
                    vid=vid,
                    step_type="summarize",
                    success_decision="summarized",
                    starting_status=VideoProcessingStatus.SUMMARIZING,
                    action=lambda: self.summarizer.summarize(
                        raw_transcript=transcript,
                        vid=vid
                    )
                )
            case "discarded":
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="discarded")

    def fetch_transcript(self, vid: Video) -> str:
        # fetch the transcript
        logger.debug(
            f"Fetching the transcript of {vid.video_id}...", 
            extra={
                "event": LogEvent.TRANSCRIPT_FETCH_STARTED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            }

        )
        transcript: str = self.transcript_service.get_transcript(vid)
        logger.debug(
            f"Finished fetching the transcript of {vid.video_id}",
            extra={
                "event": LogEvent.TRANSCRIPT_FETCH_COMPLETED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id
            }
        )
        return transcript

    def resume_downloads(self):
        # download the videos with an interrupted download
        logger.debug("Check for videos where the download got interrupted...")
        downloading_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("downloading")
        for video in downloading_vids_generator:
            try:
                vid: Video = Video.from_cache(video_db_row=video)
            except InvalidVideoError:
                raise
            logger.info(
                f"Processing video {vid.video_id} that got interrupted while downloading.",
                extra={
                    "event": LogEvent.DOWNLOAD_RESUME_STARTED,
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
                    output_path=Path(self.config.downloads.output_dir)
                ),
            )
            sleep_delay(
                calculate_delay(
                    min_delay=self.config.video_processing.min_vid_delay,
                    random_delay=self.config.video_processing.random_vid_delay
                ),
                should_sleep=self.should_sleep
            )
        logger.debug(
            "Check for videos where the download got interrupted... Done",
            extra={
                "event": LogEvent.VALIDATION_RESUME_STARTED,
            }
        )

    def resume_validations(self):
        # re-validate the videos where only the metadata is present
        logger.debug("Check for videos where the validation got interrupted...")
        validating_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("validating")
        for video in validating_vids_generator:
            vid: Video = Video.from_cache(video_db_row=video)
            logger.info(
                f"Processing video {vid.video_id} that got interrupted while validating.",
                extra={
                    "event": LogEvent.VALIDATION_RESUME_STARTED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            self.process_validation_pipeline(vid=vid, create_db_entry=False)
        logger.debug(
            "Check for videos where the validation got interrupted... Done",
            extra={
                "event": LogEvent.VALIDATION_RESUME_COMPLETED,
            }
        )

    def resume_summaries(self):
        # restart the summarization action for the videos where the summary got interrupted
        logger.debug("Check for videos where the summarization got interrupted...")
        summarizing_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("summarizing")
        for video in summarizing_vids_generator:
            vid: Video = Video.from_cache(video_db_row=video)
            logger.info(
                f"Processing video {vid.video_id} that got interrupted while summarizing.",
                extra={
                    "event": LogEvent.SUMMARIZATION_RESUME_STARTED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            try:
                transcript: str = self.fetch_transcript(vid=vid)
                if not self.execute_processing_step(
                    vid=vid,
                    step_type="summarize",
                    success_decision="summarized",
                    starting_status=VideoProcessingStatus.SUMMARIZING,
                    action=lambda: self.summarizer.summarize(
                        raw_transcript=transcript,
                        vid=vid
                    ),
                ):
                    continue
            except TranscriptError as e:
                error_msg: str = f"TranscriptError: Each transcript fetching provider failed: {str(e)}"
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
                logger.info("Moving on to the next video because of the previous TranscriptError...")
                sleep_delay(
                    calculate_delay(
                        min_delay=self.config.video_processing.min_vid_delay,
                        random_delay=self.config.video_processing.random_vid_delay
                    ),
                    should_sleep=self.should_sleep
                )
                continue
            except (SystemExit, KeyboardInterrupt):
                self.should_sleep = False
                raise # raise it to main, so that vidsift can exit
            finally:
                sleep_delay(
                    calculate_delay(
                        min_delay=self.config.video_processing.min_vid_delay,
                        random_delay=self.config.video_processing.random_vid_delay
                    ),
                    should_sleep=self.should_sleep
                )
        logger.debug(
            "Check for videos where the summarization got interrupted... Done",
            extra={
                "event": LogEvent.SUMMARIZATION_RESUME_COMPLETED,
            }
        )

    def process_validation_pipeline(self, vid: Video, create_db_entry: bool):
        if create_db_entry:
            # not process the video if a db entry exists but the video is new
            # check if the video has already been handled
            if self.video_db.exists(video_id=vid.video_id):
                logger.debug(
                    f"Skipping video with video id {vid.video_id} because it was already processed.",
                    extra={
                        "event": LogEvent.VIDEO_SKIPPED_EXISTING,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                    },
                )
                return # no delay waiting

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

        try:
            # fetch the transcript
            transcript: str = self.fetch_transcript(vid=vid)
        except TranscriptError as e:
            error_msg: str = f"TranscriptError: Each transcript fetching provider failed: {str(e)}"
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
            logger.info("Moving on to the next video because of the previous TranscriptError...")
            sleep_delay(
                calculate_delay(
                    min_delay=self.config.video_processing.min_vid_delay,
                    random_delay=self.config.video_processing.random_vid_delay
                ),
                should_sleep=self.should_sleep
            )
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
            video_validation_result = self.video_validator.validate_video(vid=vid, raw_transcript=transcript)

        except VideoValidationError as e: 
            # logs are handled by the validator, because the logs are more specific like this
            self.video_db.mark_failed(
                error_msg=repr(e),
                video_id=vid.video_id
            )
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
            reason=str(video_validation_result.summary_reason)
        )

        # take action on video based on the validation result
        self.take_action_on_video(
            vid=vid,
            video_validation_result=video_validation_result,
            transcript=transcript,
        )
        sleep_delay(
            calculate_delay(
                min_delay=self.config.video_processing.min_vid_delay,
                random_delay=self.config.video_processing.random_vid_delay
            ),
            should_sleep=self.should_sleep
        )


    def process_interrupted_videos(self):
        logger.info(
            "Starting to process interrupted videos",
            extra={"event": LogEvent.INTERRUPTED_PROCESSING_STARTED},
        )
        self.resume_validations()
        self.resume_downloads()
        self.resume_summaries()
        logger.info(
            "Completed processing interrupted videos",
            extra={
                "event": LogEvent.INTERRUPTED_PROCESSING_COMPLETED
            }
        )
