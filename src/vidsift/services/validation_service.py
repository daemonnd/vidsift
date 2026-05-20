"""
File for managing the validation process and returning the score of the video
"""
from vidsift.models.validation_result import ValidationResult
from vidsift.models.video import Video


class VideoValidator:
    def __init__(self) -> None:
        pass
    def validate_video(video: Video, transcript: str) -> ValidationResult:
        
