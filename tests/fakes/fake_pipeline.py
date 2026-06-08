from typing import Literal

from vidsift.models.validation.validation_result import ValidationResult


class FakeValidator:
    def __init__(self, decision: Literal["downloaded", "summarized", "discarded"]) -> None:
        self.decision: Literal["downloaded", "summarized", "discarded"] = decision

    def validate_video(self, vid, raw_transcript):

        return ValidationResult(
            decision=self.decision,
            content_quality_score=0.8,
            topic_match_score=0.9,
            summary_reason={"test": "test"}
        )

class FakeTranscriptService:

    def get_transcript(self, vid):

        return "hello world"

class FakeDownloader:

    def __init__(self):

        self.was_called = False

    def download(self, url, output_path):

        self.was_called = True
