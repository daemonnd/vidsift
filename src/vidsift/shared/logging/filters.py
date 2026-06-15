"""
File for making logging filters in order to apply the config values of the config
file regarding the loglevel for dependencies
"""
import logging
from logging import Filter, LogRecord


class ConsoleDependencyFilter(Filter):
    def __init__(self, console_config, name: str = "", debug_mode: bool = False) -> None:
        super().__init__(name)
        self.console_config = console_config
        self.debug_mode: bool = debug_mode

    def filter(self, record: LogRecord) -> bool | LogRecord:
        """
        Method to filter logs.
        For vidsift logs
        """
        if self.debug_mode:
            return True
        if record.name.startswith("vidsift"):
            # if it is from vidsift
            if record.levelno < logging.getLevelNamesMapping()[self.console_config.level]:
                return False
            else:
                return True
        # if it is from a dependency
        if record.levelno >= logging.getLevelNamesMapping()[self.console_config.dependency_level]:
            return True
        return False


class FileDependencyFilter(Filter):
    def __init__(self, file_config, name: str = "", debug_mode: bool = False) -> None:
        super().__init__(name)
        self.file_config = file_config
        self.debug_mode: bool = debug_mode

    def filter(self, record: LogRecord) -> bool | LogRecord:
        """
        Method to filter logs.
        For vidsift logs
        """
        if self.debug_mode:
            return True
        if record.name.startswith("vidsift"):
            # if it is from vidsift
            if record.levelno < logging.getLevelNamesMapping()[self.file_config.level]:
                return False
            else:
                return True
        # if it is from a dependency
        if record.levelno >= logging.getLevelNamesMapping()[self.file_config.dependency_level]:
            return True
        return False
