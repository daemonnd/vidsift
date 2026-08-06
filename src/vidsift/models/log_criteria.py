from pydantic import BaseModel, Field
from typing import Literal


class LogCriteria(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    contains: str
    last: int = Field(ge=1)
    format: list[str] = []
    starttime: str | None = None
    endtime: str | None = None
