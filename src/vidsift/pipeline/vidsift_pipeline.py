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



from vidsift.features.transcript.errors import TranscriptError
from vidsift.ingestion.url_collector import UrlCollector
from vidsift.models.video import Video
from vidsift.services.transcript_service import TranscriptService
from vidsift.shared.errorprotocol import logger

log: logger = logger()

class VidsiftOrchestrator:
    def __init__(self, channel_id_list: list[str]) -> None:
        # video fetching
        self.url_collector: UrlCollector = UrlCollector(channel_id_list=channel_id_list)
        # transcript
        self.transcript_service: TranscriptService = TranscriptService()

    def fetch_videos(self) -> list[Video]:
        return self.url_collector.parse_all_channels()


    def run(self) -> None:
        log.log_debug("Starting to fetch video data...")
        video_list: list[Video] = self.url_collector.parse_all_channels()
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
    vo = VidsiftOrchestrator(["UCX6OQ3DkcsbYNE6H8uQQuVA"])
    vo.run()
