"""
File for defining the format for a validation result
"""
from pydantic import BaseModel


class ValidationResult(BaseModel):
    metadata_score: int 
    total_transcript_score: int
    flags: list[str]
