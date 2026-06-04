class SummaryError(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class EmptyTranscriptSummaryError(SummaryError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
