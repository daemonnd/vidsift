"""
File for making logging filters in order to apply the config values of the config
file regarding the loglevel for dependencies
"""
import logging
from logging import Filter, LogRecord

from vidsift.config import CONFIG

console_config = CONFIG.logging.console
file_config = CONFIG.logging.file




class ConsoleDependencyFilter(Filter):
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
            # if it is from vidsift
            if record.levelno < logging.getLevelNamesMapping()[console_config.level]:
                return False
            else:
                return True
        # if it is from a dependency
        if record.levelno >= logging.getLevelNamesMapping()[console_config.dependency_level]:
            return True
        return False


class FileDependencyFilter(Filter):
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
            # if it is from vidsift
            if record.levelno < logging.getLevelNamesMapping()[file_config.level]:
                return False
            else:
                return True
        # if it is from a dependency
        if record.levelno >= logging.getLevelNamesMapping()[file_config.dependency_level]:
            return True
        return False
