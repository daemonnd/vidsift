class VideoDownloadError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class FakeDownloadError(VideoDownloadError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class OutputPathPermissionError(FakeDownloadError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class OutputPathNotFoundError(FakeDownloadError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class OutputPathIsADirectoryError(FakeDownloadError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
