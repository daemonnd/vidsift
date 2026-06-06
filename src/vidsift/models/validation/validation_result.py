from typing import Literal

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    content_quality_score: float = Field(ge=1, le=3)
    topic_match_score: float = Field(ge=1, le=3)
    decision: Literal["downloaded", "summarized", "discarded"]
    summary_reason: dict
