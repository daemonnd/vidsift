from typing import Literal

from vidsift.features.summary.errors import SummaryError
from vidsift.features.transcript.errors import TranscriptError
from vidsift.features.validation.errors import (CustomInstructionsReadingError,
                                                VideoValidationError)
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video


class FailingSummarizer:
    def __init__(self):
        self.was_called = False

    def summarize(self, raw_transcript: str, vid: Video):
        self.was_called = True
        raise SummaryError("summary failed")

class FakeValidator:
    def __init__(self, decision: Literal["downloaded", "summarized", "discarded"], should_fail: bool = False) -> None:
        self.decision: Literal["downloaded", "summarized", "discarded"] = decision
        self.was_called: bool = False
        self.should_fail: bool = should_fail

    def validate_video(self, vid, raw_transcript):
        self.was_called: bool = True
        if self.should_fail:
            raise VideoValidationError("oh, no, this failed :(")
        return ValidationResult(
            decision=self.decision,
            content_quality_score=1.7,
            topic_match_score=1.9,
            summary_reason={"test": "test"}
        )

class FakeTranscriptService:
    def get_transcript(self, vid):
        return "hello world"

class FailingTranscriptService:
    def get_transcript(self, vid):
        raise TranscriptError("oh no, this failed!")

class FakeDownloader:
    def __init__(self):
        self.was_called = False

    def download(self, video_url, output_path):
        self.was_called = True

class FakeSummarizer:
    def __init__(self) -> None:
        self.was_called = False

    def summarize(self, raw_transcript: str, vid: Video):
        self.was_called = True

class FakeInstructionProvider:
    def __init__(self):
        self.was_called = False
    def get(self, intructions_filename: str, fail: bool = False):
        self.was_called = True
        if fail:
            raise CustomInstructionsReadingError("could not read custom instructions")
        return "awesome custom instructions"
