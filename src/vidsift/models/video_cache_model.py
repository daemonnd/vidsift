from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ProcessingStatus(Enum):
    VALIDATING = "validating"
    DOWNLOADING = "downloading"
    SUMMARIZING = "summarizing"

    DONE = "done"
    FAILED = "failed"



class VideoCacheModel(BaseModel):
    video_id: str = Field(max_length=11, min_length=11)
    title: str
    url: str
    author: str
    channel_id: str
    status: ProcessingStatus
    decision: Literal["downloaded", "summarized", "discarded"] | None
    quality_score: float | None = Field(default=None, ge=0) 
    topic_match_score: float | None = Field(default=None, ge=0)
    reason: str | None
    processed_at: datetime | None

