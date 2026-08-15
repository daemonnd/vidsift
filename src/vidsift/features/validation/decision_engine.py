"""
This file exists in order to decide wether a video should be downloaded / summarized or not. 
It is using in the validation results of the metadata and transcript.
"""

from typing import Literal

from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.validation.transcript_validation_result import \
    TranscriptValidationResult
from vidsift.models.validation.validation_result import ValidationResult

# defining the decision engine constants
HIGH_TOPIC_MATCH_THRESHOLD = 2.5
HIGH_QUALITY_THRESHOLD = 2.5
MEDIUM_TOPIC_MATCH_THRESHOLD = 1.8
MEDIUM_QUALITY_THRESHOLD = 1.8


class DecisionEngine:
    def __init__(self, metadata_result: MetadataValidationResult | None, transcript_result: TranscriptValidationResult):
        self.metadata_result = metadata_result
        self.transcript_result = transcript_result

    def calculate_decision_scores(self) -> dict[str, float]:
        """
        Method to calculate the topic match and quality of metadata and transcript. 
        The scores are calculated as a weighted average of the individual scores.
        It uses the weights of 80% transcript and 20% metadata for both scores.
        It returns a dicstionary with the following structure:
        {
            "topic_match_score": float,
            "quality_score": float
        }
        """
        if self.metadata_result:
            # topic match score
            topic_match_score = (self.metadata_result.topic_match_score * 2 + self.transcript_result.topic_match_score * 8) / 10

            # quality score
            quality_score = (self.metadata_result.metadata_score * 2 + self.transcript_result.content_quality_score * 8) / 10

            return {
                "topic_match_score": topic_match_score,
                "quality_score": quality_score
            }
        else:
            return {
                "topic_match_score": self.transcript_result.topic_match_score,
                "quality_score": self.transcript_result.content_quality_score
            }

    def make_decision(self, scores: dict[str, float]) -> ValidationResult:
        """
        Method to make a decision based on the calculated scores. 
        How decisions are made:
        If the topic match score is high and the quality score is high, then download.
        If the quality score is high and the topic match score is medium, then download.

        If the quality score is medium and the topic match score is medium, then summarize.
        If the topic match score is high and the quality score is medium, then summarize.
        It the quality score is high and the topic match score is low, then summarize.

        If the topic match score is low, then discard.
        For everything else, discard.
        """

        topic_match_score = scores["topic_match_score"]
        quality_score = scores["quality_score"]

        # high topic match and high quality -> download
        if topic_match_score >= HIGH_TOPIC_MATCH_THRESHOLD and quality_score >= HIGH_QUALITY_THRESHOLD:
            return self._return_data(quality_score=quality_score, topic_match_score=topic_match_score, decision="downloaded")

        # high quality and medium topic match -> download
        elif quality_score >= HIGH_QUALITY_THRESHOLD and topic_match_score >= MEDIUM_TOPIC_MATCH_THRESHOLD:
            return self._return_data(quality_score=quality_score, topic_match_score=topic_match_score, decision="downloaded")

        # medium quality and medium topic match -> summarize
        elif quality_score >= MEDIUM_QUALITY_THRESHOLD and topic_match_score >= MEDIUM_TOPIC_MATCH_THRESHOLD:
            return self._return_data(quality_score=quality_score, topic_match_score=topic_match_score, decision="summarized")

        # low quality and high topic match -> summarize
        elif topic_match_score >= HIGH_TOPIC_MATCH_THRESHOLD and quality_score >= MEDIUM_QUALITY_THRESHOLD:
            return self._return_data(quality_score=quality_score, topic_match_score=topic_match_score, decision="summarized")

        # high quality and low topic match -> summarize
        elif quality_score >= HIGH_QUALITY_THRESHOLD and topic_match_score < MEDIUM_TOPIC_MATCH_THRESHOLD:
            return self._return_data(quality_score=quality_score, topic_match_score=topic_match_score, decision="summarized")

        # low topic match -> discard
        elif topic_match_score < MEDIUM_TOPIC_MATCH_THRESHOLD:
            return self._return_data(quality_score=quality_score, topic_match_score=topic_match_score, decision="discarded")

        # else discard
        else:
            return self._return_data(quality_score=quality_score, topic_match_score=topic_match_score, decision="discarded")

    def _return_data(
        self,
        quality_score: float,
        topic_match_score: float,
        decision: Literal["discarded", "downloaded", "summarized"],
    ) -> ValidationResult:
        if self.metadata_result is not None:
            return ValidationResult(
                    content_quality_score=quality_score, 
                    topic_match_score=topic_match_score, 
                    decision=decision, 
                    summary_reason={
                        "metadata": {
                            "reason": self.metadata_result.summary_reason,
                            "flags": self.metadata_result.flags,
                        },
                        "transcript": {
                            "reason": self.transcript_result.summary_reason,
                            "flags": self.transcript_result.flags,
                        }
                    }
                )
        else:
            return ValidationResult(
                content_quality_score=quality_score,
                topic_match_score=topic_match_score,
                decision=decision,
                summary_reason={
                    "transcript": {
                        "reason": self.transcript_result.summary_reason,
                        "flags": self.transcript_result.flags
                    }
                }
            )

