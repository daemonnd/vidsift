import logging
from json import dumps
from logging import Formatter, LogRecord
from typing import Any, Mapping

from vidsift.shared.json_utils import normalize


def get_style(levelname: str) -> str:
    level_styles: dict = {
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold red"
            }
    return level_styles.get(levelname, "white")


# def formatter for console logging handler
consoleformatter = logging.Formatter(
    "{levelname}: {message}",
    style="{"
)

class JSONFormatter(Formatter):
    def __init__(self, fmt: str | None = None, datefmt: str | None = None, style: _FormatStyle = "%", validate: bool = True, *, defaults: Mapping[str, Any] | None = None) -> None:
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        dummy = LogRecord(name='dummy', level=logging.INFO, pathname='somepath', lineno=0, msg='This is a dummy log message', args=None, exc_info=None)
        self.standard_fields = set(dummy.__dict__)
        self.standard_fields.update({"message", "asctime", "exc_text"})
        self.reserved_output_fields = {
            "timestamp",
            "level",
            "message",
            "logger_name",
            "file_name",
            "lineno",
            "exc_type",
            "exc_message",
            "exc_text",
        }
    def format(self, record: LogRecord) -> str:
        from vidsift.shared.execution_context import get_run_context
        ctx = get_run_context()
        if ctx:
            run_id = ctx.run_id
        else:
            run_id = None
        output: dict = {
                "timestamp": self.formatTime(record=record),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger_name": record.name,
                "file_name": record.filename,
                "lineno": record.lineno,
                "run_id": str(run_id),
            }
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            output["exc_type"] = str(record.exc_info[0].__name__)
            output["exc_message"] = str(record.exc_info[1])
            output["exc_text"] = str(record.exc_text)
        for key, value in record.__dict__.items():
            if key in self.standard_fields:
                continue
            if key in self.reserved_output_fields: 
                raise KeyError(f"Key {key} cannot occur twice in log output.")
            else:
                output[key] = normalize(value)


        return dumps(output)

