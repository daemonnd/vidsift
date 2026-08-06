import json
import re
from collections import deque
import logging
from time import sleep

from vidsift.config.models import AppConfig
from vidsift.features.logs.errors import (
    LogFieldMissingError,
    LogFileNotFoundError,
    LogFilePermissionError,
)
from vidsift.models.log_criteria import LogCriteria
from vidsift.shared.paths import VIDSIFT_LOG_FILE


TIMESTAMP_LEN = 23
RUN_ID_LEN = 33  # 36
LOGGER_LEN = 10
LEVEL_LEN = 7
EVENT_LEN = 40
MESSAGE_LEN = 100


class LogViewer:
    def __init__(self, config: AppConfig, log_criteria: LogCriteria) -> None:
        self.config: AppConfig = config
        self.log_criteria: LogCriteria = log_criteria

    def follow(
        self,
    ):
        try:
            with open(VIDSIFT_LOG_FILE, "r") as file:
                for line in file:
                    self._print_line(line)
                file.seek(0, 2)  # jump to end
                while True:
                    new_line = file.readline()
                    if new_line:
                        self._print_line(new_line)
                    sleep(0.1)
        except FileNotFoundError as e:
            raise LogFileNotFoundError(str(e)) from e
        except PermissionError as e:
            raise LogFilePermissionError(str(e)) from e

    def show(self):
        try:
            with open(VIDSIFT_LOG_FILE, "r") as file:
                if self.log_criteria.last > 0:
                    lines = deque(
                        file,
                        maxlen=self.log_criteria.last,
                    )
                else:
                    lines = file

                for line in lines:
                    self._print_line(line)

        except FileNotFoundError as e:
            raise LogFileNotFoundError(str(e)) from e
        except PermissionError as e:
            raise LogFilePermissionError(str(e)) from e

    def _print_line(self, line: str):
        line_data = json.loads(line)
        display = self._filter_line(line_data)
        if not display:
            return
        print(self._format(line_data))

    def _filter_line(self, line_data: dict) -> bool:
        """
        Method that takes a line and compares it to the
        given log criteria.
        If the line matches the criteria, it gets returns True.
        If not, it returns False
        """
        # if the log level is high enough
        if getattr(logging, line_data["level"]) >= getattr(
            logging, self.log_criteria.level
        ):
            if (
                self.log_criteria.contains in line_data["event"]
                or self.log_criteria.contains in line_data["message"]
            ):
                return True
        return False

    def _format(self, line_data: dict) -> str:
        try:
            timestamp = line_data["timestamp"][:TIMESTAMP_LEN]
            level = f"{line_data['level']:<7}"
            message = line_data["message"][:MESSAGE_LEN]
            event = line_data["event"][:EVENT_LEN]
            event = f"{event:<{EVENT_LEN}}"
            run_id = line_data["run_id"][:RUN_ID_LEN]
            run_id = f"{run_id:<{RUN_ID_LEN}}"
            logger = f"{line_data['logger_name'][:LOGGER_LEN]:<{LOGGER_LEN}}"
            values = {
                "$timestamp": timestamp,
                "$level": level,
                "$run_id": run_id,
                "$event": event,
                "$logger": logger,
                "$message": message,
            }
        except KeyError as e:
            raise LogFieldMissingError(str(e)) from e

        output = " ".join(self.log_criteria.format)

        for placeholder, value in values.items():
            output = output.replace(placeholder, value)
        if "$" in output:
            raise

        return output
