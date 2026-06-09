class VideoProcessingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class VideoProcessingDataValidationError(VideoProcessingError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class DBWritingError(VideoProcessingError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
