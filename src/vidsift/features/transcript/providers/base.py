from typing import Protocol

from vidsift.models.video import Video


class TranscriptProvider(Protocol):
    def get_transcript(self, video: Video) -> str:
        ...
    def get_provider_name(self) -> str:
        ...
