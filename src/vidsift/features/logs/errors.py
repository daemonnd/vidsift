class LogDisplayError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class LogFileNotFoundError(LogDisplayError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class LogFilePermissionError(LogDisplayError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class LogFieldMissingError(LogDisplayError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
