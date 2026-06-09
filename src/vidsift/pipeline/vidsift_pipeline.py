
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
from dataclasses import asdict
from pathlib import Path
from sys import exit
from typing import Generator

from vidsift.config import CONFIG
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

logger = logging.getLogger(__name__)

class VidsiftOrchestrator:
    def __init__(
        self,
        channel_id_list: list[str],
        video_validator: VideoValidator | None = None,
        transcript_service: TranscriptService | None = None,
        summarizer: SummarizationService | None = None,
        downloader: VideoDownloader | None = None,
        video_db: VideoProcessingRepository | None = None,

    ):
        # video fetching
        self.video_data_collector: VideoDataCollection = VideoDataCollection(channel_id_list=channel_id_list)
        # video cache
        self.video_db: VideoProcessingRepository = (video_db or VideoProcessingRepository())
        # validation
        self.video_validator: VideoValidator = (video_validator or VideoValidator())
        # transcript
        self.transcript_service: TranscriptService = (transcript_service or TranscriptService())
        # summarization
        self.summarizer: SummarizationService = (summarizer or SummarizationService())
        # downloading
        self.downloader: VideoDownloader = (downloader or VideoDownloader())

    def run(self) -> None:
        try:
            # before fetching and processing any new videos, process the interrupted / failed ones
            self.process_interrupted_videos()

            # new videos
            try:
                video_generator: Generator[Video, None, None] = self.video_data_collector.get_videos_to_process()
            except VideoDataCollectionError as e:
                logger.critical(f"VideoDataCollectionError: Failed to collect the necessary data about the videos to process: {str(e)}")
                logger.info("Exiting because no data exist...")
                exit(1)
            logger.debug("Starting to iterate over each video and perform the validation action...")

            for vid in video_generator:
                self.process_validation_pipeline(vid=vid, create_db_entry=True)

        finally:
            self.video_db.close()

    def validate_video(self, vid: Video, raw_transcript: str):
        # validate the video and get the action to perform
        video_validation_result: ValidationResult = self.video_validator.validate_video(vid=vid, raw_transcript=raw_transcript)

        logger.debug(f"current status: {self.video_db.get(vid.video_id)}")
        return video_validation_result

    def download(self, vid: Video):
        logger.info(f"Downloading video {asdict(vid)} with id {vid.video_id}...")
        self.downloader.download(vid.url, output_path=Path(CONFIG.downloads.output_dir))

    def summarize(self, vid: Video, transcript: str):
        logger.info(f"Video {asdict(vid)} with id {vid.video_id} will be summarized.")
        self.summarizer.summarize(raw_transcript=transcript)

    def take_action_on_video(self, video_validation_result: ValidationResult, transcript: str, vid: Video):
        # take the appropriate action based on the validation result
        match video_validation_result.decision:
            case "downloaded":
                self.download(vid=vid)
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="downloaded")
            case "summarized":
                self.summarize(vid=vid, transcript=transcript)
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="summarized")
            case "discarded":
                logger.info(f"Video {asdict(vid)} with id {vid.video_id} will be discarded.")
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="discarded")


    def fetch_transcript(self, vid: Video):
        # fetch the transcript
        logger.debug(f"Fetching the transcript of {vid.video_id}...")
        return self.transcript_service.get_transcript(vid)

    def resume_downloads(self):
        # download the videos with an interrupted download
        logger.debug("Check for videos where the download got interrupted...")
        downloading_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("downloading")
        for video in downloading_vids_generator:
            vid: Video = Video.from_cache(video_db_row=video)
            self.download(vid=vid)
            # add it to the video cache
            self.video_db.update_after_done(video_id=vid.video_id, decision="downloaded")
        logger.debug("Check for videos where the download got interrupted... Done")

    def resume_validations(self):
        # re-validate the videos where only the metadata is present
        logger.debug("Check for videos where the validation got interrupted...")
        validating_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("validating")
        for video in validating_vids_generator:
            vid: Video = Video.from_cache(video_db_row=video)
            self.process_validation_pipeline(vid=vid, create_db_entry = False)
        logger.debug("Check for videos where the validation got interrupted... Done")

    def resume_summaries(self):
        # restart the summarization action for the videos where the summary got interrupted
        logger.debug("Check for videos where the summarization got interrupted...")
        summarizing_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("summarizing")
        for video in summarizing_vids_generator:
            vid: Video = Video.from_cache(video_db_row=video)
            try:
                transcript: str = self.fetch_transcript(vid=vid)
                self.summarize(vid=vid, transcript=transcript)
                # add it to the video cache
                self.video_db.update_after_done(video_id=vid.video_id, decision="summarized")
            except TranscriptError as e:
                error_msg: str = f"TranscriptError: Each transcript fetching provider failed: {str(e)}"
                logger.error(error_msg)
                # add the failure to the video database
                self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
                logger.info("Moving on to the next video because of the previous TranscriptError...")
                continue
            except SummaryError as e:
                error_msg: str = f"SummaryError: Failed to summarize the video with id {vid.video_id} because of the following error: {str(e)}"
                logger.error(error_msg)
                # add the failure to the video database
                self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
                logger.info("Moving on to the next video because of the previous SummaryError...")
                continue
        logger.debug("Check for videos where the summarization got interrupted... Done")


    def process_validation_pipeline(self, vid: Video, create_db_entry: bool):
        try:
            if create_db_entry:
                # not process the video if a db entry exists but the video is new
                # check if the video has already been handled
                if self.video_db.exists(video_id=vid.video_id):
                    return

                # update the database, set the status to VALIDATING
                # only do that for new videos
                self.video_db.create(vid=vid)
                logger.debug(f"current status: {self.video_db.get(vid.video_id)}")

            # fetch the transcript
            transcript: str = self.fetch_transcript(vid=vid)

            # get the validation result
            video_validation_result = self.validate_video(vid=vid, raw_transcript=transcript)
            # update the database after validation
            self.video_db.save_validation_result(
                video_id=vid.video_id,
                decision=video_validation_result.decision,
                quality_score=video_validation_result.content_quality_score,
                topic_match_score=video_validation_result.topic_match_score,
                reason=str(video_validation_result.summary_reason)
            )

            # take action on video based on the validation result
            self.take_action_on_video(vid=vid, video_validation_result=video_validation_result, transcript=transcript)


        except TranscriptError as e:
            error_msg: str = f"TranscriptError: Each transcript fetching provider failed: {str(e)}"
            logger.error(error_msg)
            # add the failure to the video database
            self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
            logger.info("Moving on to the next video because of the previous TranscriptError...")
            return
        except VideoValidationError as e:
            error_msg: str = f"VideoValidationError: Failed to validate the video with id {vid.video_id} because of the following error: {str(e)}"
            logger.error(error_msg)
            # add the failure to the video database
            self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
            logger.info("Moving on to the next video because of the previous VideoValidationError...")
            return
        except SummaryError as e:
            error_msg: str = f"SummaryError: Failed to summarize the video with id {vid.video_id} because of the following error: {str(e)}"
            logger.error(error_msg)
            # add the failure to the video database
            self.video_db.mark_failed(error_msg=error_msg, video_id=vid.video_id)
            logger.info("Moving on to the next video because of the previous SummaryError...")
            return

    def process_interrupted_videos(self):
        self.resume_validations()
        self.resume_downloads()
        self.resume_summaries()

        # for another PR
        #failed_vids_generator: Generator[VideoProcessingRecord, None, None] = self.video_db.get_by_status("failed")



if __name__ == "__main__":
    vo = VidsiftOrchestrator(["UCo71RUe6DX4w-Vd47rFLXPg"])
    vo.run()
