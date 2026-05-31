from typing import Literal

from pydantic import BaseModel, Field


class TranscriptValidationResult(BaseModel):
    content_quality_score: int = Field(ge=1, le=3)
    topic_match_score: int = Field(ge=1, le=3)
    confidence: int = Field(ge=1, le=3)
    flags: set[
        Literal[
            "low_substance",
            "excessive_self_promotion",
            "fear_mongering",
            "manipulative_persuasion",
            "off_topic",
            "repetitive_content"
        ]
    ]
    summary_reason: str
