from typing import Generator, Literal

from vidsift.config.models import AppConfig
from vidsift.features.summary.errors import SummaryError
from vidsift.features.transcript.errors import TranscriptError
from vidsift.features.validation.errors import (CustomInstructionsReadingError,
                                                VideoValidationError)
from vidsift.ingestion.errors import VideoDataCollectionError
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.shared.video_discovery_source import DiscoverySource


class FakeDataCollector:
    def __init__(self, channel_id_list: list[str], config: AppConfig, videos: list[tuple[Video, DiscoverySource]]) -> None:
        self.config = config
        self.channel_id_list = channel_id_list
        self.fetched_videos: int = 0
        self.videos = videos
        if not self.channel_id_list:
            raise VideoDataCollectionError(
                "The given channel id list is empty, no data can be collected"
            )
    def get_videos_to_process(self) -> Generator[tuple[Video, DiscoverySource], None, None]:
        for vid in self.videos:
            self.fetched_videos += 1
            yield vid

class FakeVideoFilter:
    def __init__(self, config) -> None:
        pass
    def check_is_livestream(self, vid: Video, is_livestream: bool = False) -> bool:
        return is_livestream

class FailingSummarizer:
    def __init__(self):
        self.summarize_calls = 0

    def summarize(self, raw_transcript: str, vid: Video):
        self.summarize_calls += 1
        raise SummaryError("summary failed")

class FakeValidator:
    def __init__(
        self,
        decision: Literal["downloaded", "summarized", "discarded"] | None = None,
        decisions: list[Literal["downloaded", "summarized", "discarded"]] | None = None,
        should_fail: bool = False,
    ):
        self.decision = decision
        self.decisions = decisions or []
        self.validate_calls = 0
        self.should_fail = should_fail

    def validate_video(self, vid, raw_transcript):
        self.validate_calls += 1

        if self.should_fail:
            raise VideoValidationError("oh no")

        if self.decisions:
            decision = self.decisions.pop(0)
        else:
            decision = self.decision

        return ValidationResult(
            decision=decision,
            content_quality_score=2.5,
            topic_match_score=2.7,
            summary_reason={"test": "test"},
        )

class FakeTranscriptService:
    def __init__(self) -> None:
        self.transcript_calls = 0
    def get_transcript(self, vid):
        self.transcript_calls += 1
        return "hello world"

class FailingTranscriptService:
    def __init__(self) -> None:
        self.transcript_calls = 0
    def get_transcript(self, vid):
        self.transcript_calls += 1
        raise TranscriptError("Failed to fetch the transcript with all providers")

class FakeDownloader:
    def __init__(self):
        self.was_called = False
        self.download_calls = 0

    def download(self, video_url, output_path):
        self.was_called = True
        self.download_calls += 1

class FakeSummarizer:
    def __init__(self) -> None:
        self.was_called = False
        self.summarize_calls = 0

    def summarize(self, raw_transcript: str, vid: Video):
        self.summarize_calls += 1
        self.was_called = True

class FakeInstructionProvider:
    def __init__(self):
        self.was_called = False
        self.instruction_provider_called = 0
    def get(self, intructions_filename: str, fail: bool = False):
        self.was_called = True
        self.instruction_provider_called += 1
        if fail:
            raise CustomInstructionsReadingError("could not read custom instructions")
        return "awesome custom instructions"
