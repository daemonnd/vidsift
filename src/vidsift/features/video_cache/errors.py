class VideoCacheError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class VCDataValidationError(VideoCacheError):
    """VC = VideoCache"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class DBWritingError(VideoCacheError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
