"""
Custom errors of vidsift related to the transcripts
"""

class TranscriptError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TranscriptNotAvailibleError(TranscriptError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TranscriptDownloadError(TranscriptError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TranscriptFetchingError(TranscriptError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TranscriptFetchingBlockedError(TranscriptError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TranscriptNotFoundError(TranscriptError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class VTTFileReadingError(TranscriptError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


