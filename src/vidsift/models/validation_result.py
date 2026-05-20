"""
    File for defining the format for a validation result
"""
from dataclasses import dataclass


@dataclass
class ValidationResult:
    final_score: float
    metadata_score: int
    total_transcript_score: int
    flags: list[str]
