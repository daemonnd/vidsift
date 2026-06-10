import logging
from logging import Filter, LogRecord


class DependencyFilter(Filter):
    def __init__(self, name: str = "", debug_mode: bool = False) -> None:
        super().__init__(name)
        self.debug_mode: bool = debug_mode

    def filter(self, record: LogRecord) -> bool | LogRecord:
        """
        Method to filter logs.
        For vidsift logs
        """
        if self.debug_mode:
            return True
        if record.name.startswith("vidsift"):
            if record.levelno < logging.INFO:
                return False
            else:
                return True
        if record.levelno >= logging.WARNING:
            return True
        return False
