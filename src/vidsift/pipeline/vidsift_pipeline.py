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



from sys import exit

from vidsift.features.transcript.errors import TranscriptError
from vidsift.ingestion.errors import VideoDataCollectionError
from vidsift.models.video import Video
from vidsift.services.transcript_service import TranscriptService
from vidsift.services.video_data_collection_service import VideoDataCollection
from vidsift.shared.errorprotocol import logger

log: logger = logger()

class VidsiftOrchestrator:
    def __init__(self, channel_id_list: list[str]) -> None:
        # video fetching
        self.video_data_collector: VideoDataCollection = VideoDataCollection(channel_id_list=channel_id_list)
        # transcript
        self.transcript_service: TranscriptService = TranscriptService()

    def fetch_videos(self) -> list[Video]:
        return self.video_data_collector.get_videos_to_process()


    def run(self) -> None:
        log.log_debug("Starting to fetch video data...")
        try:
            video_list: list[Video] = self.fetch_videos()
        except VideoDataCollectionError as e:
            log.log_critical(f"VideoDataCollectionError: Failed to collect the necessary data about the videos to process: {str(e)}")
            log.log_info("Exiting because no data exist...")
            exit(1)
        print(f"video list: {video_list}")
        log.log_debug("Starting to iterate over each video and perform the validation action...")
        for vid in video_list:
            try:
                log.log_debug(f"Fetching the transcript of {vid.video_id}...")
                transcript: str = self.transcript_service.get_transcript(vid)
                print(transcript)
            except TranscriptError as e:
                log.log_error(f"TranscriptError: Each transcript fetching provider failed: {str(e)}")




if __name__ == "__main__":
    vo = VidsiftOrchestrator(["UC9x0AN7BWHpCDHSm9NiJFJQ"])
    vo.run()
