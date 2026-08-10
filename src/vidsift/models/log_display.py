from pydantic import BaseModel, Field
from typing import Literal


class LogDisplayOpts(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    contains: str
    last: int = Field(ge=1)
    format: list[str] = []
    colors: bool
    all_files: bool
