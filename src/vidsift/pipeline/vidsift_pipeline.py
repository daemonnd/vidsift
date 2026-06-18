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
from pathlib import Path
from sys import exit
from typing import Generator

from vidsift.config.models import AppConfig
from vidsift.features.download.downloader import VideoDownloader
from vidsift.features.summary.errors import SummaryError
from vidsift.features.transcript.errors import TranscriptError
from vidsift.features.validation.errors import VideoValidationError
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.ingestion.errors import VideoDataCollectionError
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.models.video_record import VideoProcessingRecord
from vidsift.services.summarization_service import SummarizationService
from vidsift.services.transcript_service import TranscriptService
from vidsift.services.validation_service import VideoValidator
from vidsift.services.video_data_collection_service import VideoDataCollection
from vidsift.shared.delay_calculator import calculate_delay, sleep_delay
from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)


class VidsiftOrchestrator:
    def __init__(
        self,
        channel_id_list: list[str],
        config: AppConfig,
        video_validator: VideoValidator | None = None,
        transcript_service: TranscriptService | None = None,
        summarizer: SummarizationService | None = None,
        downloader: VideoDownloader | None = None,
        video_db: VideoProcessingRepository | None = None,
        should_sleep: bool = True
    ):
        self.config: AppConfig = config
        # video fetching
        self.video_data_collector: VideoDataCollection = VideoDataCollection(channel_id_list=channel_id_list)
        # video cache
        self.video_db: VideoProcessingRepository = (video_db or VideoProcessingRepository(config=self.config))
        # validation
        self.video_validator: VideoValidator = (video_validator or VideoValidator(config))
        # transcript
        self.transcript_service: TranscriptService = (transcript_service or TranscriptService())
        # summarization
        self.summarizer: SummarizationService = (summarizer or SummarizationService(config))
        # downloading
        self.downloader: VideoDownloader = (downloader or VideoDownloader())

        # delay 
        self.should_sleep: bool = should_sleep

    def run(self) -> None:
        try:
            logger.info(
                "The vidsift orchestrator started.",
                extra={"event": LogEvent.ORCHESTRATOR_STARTED},
            )  # TODO: add debug mode when cli is implemented

            # before fetching and processing any new videos, process the interrupted / failed ones
            self.process_interrupted_videos()

            # new videos
            try:
                logger.debug("RSS Fetch completed",
                    extra={
                        "event": LogEvent.RSS_FETCH_STARTED,
                    }
                )
                video_generator: Generator[Video, None, None] = self.video_data_collector.get_videos_to_process()
            except VideoDataCollectionError as e:
                logger.exception(
                    f"VideoDataCollectionError: Failed to collect the necessary data about the videos to process: {str(e)}",
                    extra={"event": LogEvent.RSS_FETCH_FAILED},
                )
                logger.info("Exiting because no data exist...")
                exit(1)


            for vid in video_generator:
                self.process_validation_pipeline(vid=vid, create_db_entry=True)

        finally:
            self.video_db.close()
            logger.info(
                "The vidsift orchestrator has been stopped.",
                extra={"event": LogEvent.ORCHESTRATOR_STOPPED},
            )

    def validate_video(self, vid: Video, raw_transcript: str):
        # validate the video and get the action to perform
        video_validation_result: ValidationResult = self.video_validator.validate_video(
            vid=vid,
            raw_transcript=raw_transcript,
        )
        return video_validation_result

    def download(self, vid: Video):
        logger.info(
            "Starting video download.",
            extra={
                "event": LogEvent.VIDEO_DOWNLOAD_STARTED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )
        self.downloader.download(vid.url, output_path=Path(self.config.downloads.output_dir))
        logger.info(
            "Video download completed.",
            extra={
                "event": LogEvent.VIDEO_DOWNLOAD_COMPLETED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )

    def summarize(self, vid: Video, transcript: str):
        logger.info(
            "Starting video summarization.",
            extra={
                "event": LogEvent.VIDEO_SUMMARIZATION_STARTED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )
        self.summarizer.summarize(raw_transcript=transcript, vid=vid)
        logger.info(
            "Video summarization completed.",
            extra={
                "event": LogEvent.VIDEO_SUMMARIZATION_COMPLETED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )

    def take_action_on_video(self, video_validation_result: ValidationResult, transcript: str, vid: Video):
        # take the appropriate action based on the validation result
        match video_validation_result.decision:
            case "downloaded":
                self.download(vid=vid)
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="downloaded")
                logger.info(
                    "Video processing completed.",
                    extra={
                        "event": LogEvent.VIDEO_PROCESSING_COMPLETED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                        "decision": "downloaded",
                    },
                )
            case "summarized":
                self.summarize(vid=vid, transcript=transcript)
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="summarized")
                logger.info(
                    "Video processing completed.",
                    extra={
                        "event": LogEvent.VIDEO_PROCESSING_COMPLETED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                        "decision": "summarized",
                    },
                )
            case "discarded":
                logger.info(
                    "Video discarded.",
                    extra={
                        "event": LogEvent.VIDEO_PROCESSING_COMPLETED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                        "decision": "discarded",
                    },
                )
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="discarded")

    def fetch_transcript(self, vid: Video):
        # fetch the transcript
        logger.debug(
            f"Fetching the transcript of {vid.video_id}...", 
            extra={
                "event": LogEvent.TRANSCRIPT_FETCH_STARTED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            }

        )
        return self.transcript_service.get_transcript(vid)

    def resume_downloads(self):
        # download the videos with an interrupted download
        logger.debug("Check for videos where the download got interrupted...")
        downloading_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("downloading")
        for video in downloading_vids_generator:
            vid: Video = Video.from_cache(video_db_row=video)
            logger.info(
                f"Processing video {vid.video_id} that got interrupted while downloading.",
                extra={
                    "event": LogEvent.DOWNLOAD_RESUME_STARTED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            self.download(vid=vid)
            # add it to the video cache
            self.video_db.update_after_done(video_id=vid.video_id, decision="downloaded")
            logger.info(
                "Video processing completed.",
                extra={
                    "event": LogEvent.VIDEO_PROCESSING_COMPLETED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "decision": "downloaded",
                },
            )
            sleep_delay(
                calculate_delay(
                    min_delay=self.config.video_processing.min_vid_delay,
                    random_delay=self.config.video_processing.random_vid_delay
                ),
                should_sleep=self.should_sleep
            )
        logger.debug("Check for videos where the download got interrupted... Done")

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
        logger.debug("Check for videos where the validation got interrupted... Done")

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
                self.summarize(vid=vid, transcript=transcript)
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="summarized")
                logger.info(
                    "Video processing completed.",
                    extra={
                        "event": LogEvent.VIDEO_PROCESSING_COMPLETED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                        "decision": "summarized",
                    },
                )
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
                continue
            except SummaryError as e:
                error_msg: str = f"SummaryError: Failed to summarize the video with id {vid.video_id} because of the following error: {str(e)}"
                logger.exception(
                    error_msg,
                    extra={
                        "event": LogEvent.VIDEO_SUMMARIZATION_FAILED,
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                    },
                )
                # add the failure to the video database
                self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
                logger.info("Moving on to the next video because of the previous SummaryError...")
                continue
            finally:
                sleep_delay(
                    calculate_delay(
                        min_delay=self.config.video_processing.min_vid_delay,
                        random_delay=self.config.video_processing.random_vid_delay
                    ),
                    should_sleep=self.should_sleep
                )
        logger.debug("Check for videos where the summarization got interrupted... Done")

    def process_validation_pipeline(self, vid: Video, create_db_entry: bool):
        try:
            if create_db_entry:
                # not process the video if a db entry exists but the video is new
                # check if the video has already been handled
                if self.video_db.exists(video_id=vid.video_id):
                    logger.info(
                        "Skipping video because it was already processed.",
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

            # fetch the transcript
            transcript: str = self.fetch_transcript(vid=vid)

            # get the validation result
            video_validation_result = self.validate_video(vid=vid, raw_transcript=transcript)
            logger.info(
                f"Video validation completed with decision '{video_validation_result.decision}'.",
                extra={
                    "event": LogEvent.VIDEO_VALIDATION_COMPLETED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "decision": video_validation_result.decision,
                    "quality_score": video_validation_result.content_quality_score,
                    "topic_match_score": video_validation_result.topic_match_score,
                    "summary_reason": video_validation_result.summary_reason,
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
            return
        except VideoValidationError as e:
            error_msg: str = f"VideoValidationError: Failed to validate the video with id {vid.video_id} because of the following error: {str(e)}"
            logger.exception(
                error_msg,
                extra={
                    "event": LogEvent.VIDEO_VALIDATION_FAILED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            # add the failure to the video database
            self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
            logger.info("Moving on to the next video because of the previous VideoValidationError...")
            return
        except SummaryError as e:
            error_msg: str = f"SummaryError: Failed to summarize the video with id {vid.video_id} because of the following error: {str(e)}"
            logger.exception(
                error_msg,
                extra={
                    "event": LogEvent.VIDEO_SUMMARIZATION_FAILED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )
            # add the failure to the video database
            self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
            logger.info("Moving on to the next video because of the previous SummaryError...")
            return
        finally:
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

        # for another PR
        # failed_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("failed")


if __name__ == "__main__":
    vo = VidsiftOrchestrator(["UCo71RUe6DX4w-Vd47rFLXPg"])
    vo.run()
