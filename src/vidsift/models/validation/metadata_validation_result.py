from typing import Literal

from pydantic import BaseModel, Field


class MetadataValidationResult(BaseModel):
    metadata_score: int = Field(ge=0, le=100)
    topic_match_score: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
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
