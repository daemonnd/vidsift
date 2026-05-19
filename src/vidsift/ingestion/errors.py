class VideoDataCollectionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidHTTPStatusError(VideoDataCollectionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NonWellFormattedFeedError(VideoDataCollectionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
