from dataclasses import dataclass


@dataclass
class PreValidationResult:
    title_emoji_count: int
    title_uppercase_ratio: float
    title_char_length: int
    title_emoji_list: list[str]
    title_clickbait_patters: int
    transcript_clickbait_patterns: int

