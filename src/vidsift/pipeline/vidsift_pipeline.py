
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


from dataclasses import asdict
from pathlib import Path
from sys import exit
from typing import Generator, Literal

from vidsift.config import CONFIG
from vidsift.features.download.downloader import VideoDownloader
from vidsift.features.summary.errors import SummaryError
from vidsift.features.transcript.errors import TranscriptError
from vidsift.features.validation.errors import VideoValidationError
from vidsift.features.video_cache.repository import VideoCacheRepository
from vidsift.ingestion.errors import VideoDataCollectionError
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.services.summarization_service import SummarizationService
from vidsift.services.transcript_service import TranscriptService
from vidsift.services.validation_service import VideoValidator
from vidsift.services.video_data_collection_service import VideoDataCollection
from vidsift.shared.errorprotocol import logger

log: logger = logger()

class VidsiftOrchestrator:
    def __init__(self, channel_id_list: list[str]) -> None:
        # video fetching
        self.video_data_collector: VideoDataCollection = VideoDataCollection(channel_id_list=channel_id_list)
        # video cache
        self.video_cache: VideoCacheRepository = VideoCacheRepository()
        # validation
        self.video_validator: VideoValidator = VideoValidator()
        # transcript
        self.transcript_service: TranscriptService = TranscriptService()
        # summarization
        self.summarizer: SummarizationService = SummarizationService()
        # downloading
        self.downloader: VideoDownloader = VideoDownloader()
    @log.log
    def run(self) -> None:
        try:
            try:
                video_generator: Generator[Video, None, None] = self.video_data_collector.get_videos_to_process()
            except VideoDataCollectionError as e:
                log.log_critical(f"VideoDataCollectionError: Failed to collect the necessary data about the videos to process: {str(e)}")
                log.log_info("Exiting because no data exist...")
                exit(1)
            log.log_debug("Starting to iterate over each video and perform the validation action...")
            for vid in video_generator:
                try:
                    # check if the video has already been handled
                    if self.video_cache.exists(video_id=vid.video_id):
                        continue
                    # fetch the transcript
                    log.log_debug(f"Fetching the transcript of {vid.video_id}...")
                    transcript: str = self.transcript_service.get_transcript(vid)

                    # validate the video and get the action to perform
                    video_validation_result: ValidationResult = self.video_validator.validate_video(vid=vid, raw_transcript=transcript)

                    # take the appropriate action based on the validation result
                    match video_validation_result.decision:
                        case "downloaded":
                            log.log_info(f"Downloading video {asdict(vid)} with id {vid.video_id}...")
                            self.downloader.download(vid.url, output_path=Path(CONFIG.downloads.output_dir))
                            # add it to the video cache
                            self.video_cache.save(
                                vid=vid, decision="downloaded", 
                                quality_score=video_validation_result.content_quality_score, 
                                topic_match_score=video_validation_result.topic_match_score,
                                reason=str(video_validation_result.summary_reason)
                            )
                        case "summarized":
                            log.log_info(f"Video {asdict(vid)} with id {vid.video_id} will be summarized.")
                            self.summarizer.summarize(raw_transcript=transcript)
                            # add it to the video cache
                            self.video_cache.save(
                                vid=vid, decision="summarized", 
                                quality_score=video_validation_result.content_quality_score, 
                                topic_match_score=video_validation_result.topic_match_score,
                                reason=str(video_validation_result.summary_reason)
                            )
                        case "discarded":
                            log.log_info(f"Video {asdict(vid)} with id {vid.video_id} will be discarded.")
                            # add it to the video cache
                            self.video_cache.save(
                                vid=vid, decision="discarded", 
                                quality_score=video_validation_result.content_quality_score, 
                                topic_match_score=video_validation_result.topic_match_score,
                                reason=str(video_validation_result.summary_reason)
                            )
                except TranscriptError as e:
                    log.log_error(f"TranscriptError: Each transcript fetching provider failed: {str(e)}")
                    log.log_info("Moving on to the next video because of the previous TranscriptError...")
                    continue
                except VideoValidationError as e:
                    log.log_error(f"VideoValidationError: Failed to validate the video with id {vid.video_id} because of the following error: {str(e)}")
                    log.log_info("Moving on to the next video because of the previous VideoValidationError...")
                    continue
                except SummaryError as e:
                    log.log_error(f"SummaryError: Failed to summarize the video with id {vid.video_id} because of the following error: {str(e)}")
                    log.log_info("Moving on to the next video because of the previous SummaryError...")
                    continue
        finally:
            self.video_cache.close()




if __name__ == "__main__":
    vo = VidsiftOrchestrator(["UC9x0AN7BWHpCDHSm9NiJFJQ"])
    vo.run()
