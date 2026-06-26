"""
Custom Errors of vidsift related to video validation
"""

class VideoValidationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NoMiddleChunkError(VideoValidationError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class EmptyTranscriptError(VideoValidationError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class CustomInstructionsReadingError(VideoValidationError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
