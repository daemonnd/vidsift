from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class VideoCacheModel(BaseModel):
    video_id: str
    title: str
    author: str
    channel_id: str
    decision: Literal["downloaded", "summarized", "discarded"]
    quality_score: float = Field(ge=0)
    topic_match_score: float = Field(ge=0)
    reason: str
    processed_at: datetime
