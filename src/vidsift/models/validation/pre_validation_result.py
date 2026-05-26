from dataclasses import dataclass


@dataclass
class PreValidationResult:
    title_emoji_ratio: float
    title_uppercase_ratio: float
    title_punctuation_ratio: float
    title_clickbait_phrases: int
    transcript_clickbait_phrases: int

