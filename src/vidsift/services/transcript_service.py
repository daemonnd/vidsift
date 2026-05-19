from vidsift.features.transcript.errors import TranscriptError
from vidsift.features.transcript.providers.base import TranscriptProvider
from vidsift.features.transcript.providers.transcript_api_provider import \
    YoutubeTranscriptApiProvider
from vidsift.features.transcript.providers.yt_dlp_provider import \
    YtDlpTranscriptProvider
from vidsift.models.video import Video
from vidsift.shared.errorprotocol import logger

log: logger = logger()


class TranscriptService:
    def __init__(self) -> None:
        self.providers: list[TranscriptProvider] = [YtDlpTranscriptProvider(), YoutubeTranscriptApiProvider()]

    def get_transcript(self, video: Video) -> str:
        for provider in self.providers:
            try:
                return provider.get_transcript(video)
            except TranscriptError as e:
                log.log_warning(f"TranscriptError: Failed to fetch the transcript with the current provider {provider.get_provider_name()}: {str(e)}")
            except Exception as e:
                log.log_warning(f"Exception: Failed to fetch the transcript with the current provider {provider.get_provider_name()}: {str(e)}")

        raise TranscriptError("Failed to fetch the transcript with all providers")

