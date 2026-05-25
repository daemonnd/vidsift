from typing import Literal

from pydantic import BaseModel, Field


class MetadataValidationResult(BaseModel):
    metadata_score: int = Field(ge=1, le=3)
    topic_match_score: int = Field(ge=1, le=3)
    confidence: int = Field(ge=1, le=3)
    flags: set[
            Literal[
            "fake_urgency",
            "excessive_hype",
            "sensationalism",
            "spam_tone",
            "suspicious_certainty",
            "low_topic_match"
        ]
    ]
    summary_reason: str
