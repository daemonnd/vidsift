import json
import sys
from logging import LogRecord, getLogger
from pathlib import Path

import pytest

from vidsift.shared.logging.formatters import JSONFormatter


@pytest.fixture()
def json_formatter():
    return JSONFormatter()

@pytest.fixture()
def log():
    return getLogger(__name__)

def test_no_extra_format(log, json_formatter):
    formatter: JSONFormatter = json_formatter
    record = LogRecord(name="vidsift", level=20, pathname="pathtopath", lineno=5, msg="this is an info", func="randomfunc", sinfo="some sinfo", args=None, exc_info=None)

    output = formatter.format(record=record)

    parsed = json.loads(output)

    assert parsed["message"] == "this is an info"
    assert parsed["level"] == "INFO"
    assert parsed["lineno"] == 5

    with pytest.raises(KeyError):
        assert parsed["exc_info"] is None

def test_small_extra_format(log, json_formatter):
    formatter: JSONFormatter = json_formatter
    record = LogRecord(name="vidsift", level=20, pathname="pathtopath", lineno=5, msg="this is an info", func="randomfunc", sinfo="some sinfo", args=None, exc_info=None)
    record.video_id = "someid"
    record.channel_id = "channel_id"
    record.somepath = Path.home()

    output = formatter.format(record=record)

    parsed = json.loads(output)

    assert parsed["video_id"] == "someid"
    assert parsed["channel_id"] == "channel_id"
    assert parsed["somepath"] == str(Path.home())

def test_exception_output_format(log, json_formatter):
    formatter: JSONFormatter = json_formatter
    record = LogRecord(name="vidsift", level=20, pathname="pathtopath", lineno=5, msg="this is an info", func="randomfunc", sinfo="some sinfo", args=None, exc_info=None)
    record.video_id = "someid"
    record.channel_id = "channel_id"
    record.timestamp = "something"

    with pytest.raises(KeyError):
        output = formatter.format(record=record)

def test_exception_formatting(log, json_formatter):
    try:
        7/0
    except ZeroDivisionError as e:
        exc_info = sys.exc_info()

    formatter: JSONFormatter = json_formatter
    record = LogRecord(name="vidsift", level=20, pathname="pathtopath", lineno=5, msg="this is an info", func="randomfunc", sinfo="some sinfo",  args=None, exc_info=exc_info)
    record.video_id = "someid"
    record.channel_id = "channel_id"
    
    output = formatter.format(record=record)

    parsed = json.loads(output)

    assert parsed["exc_type"] == "ZeroDivisionError"
    assert parsed["exc_message"] == "division by zero"
    assert str(parsed["exc_text"]).endswith("ZeroDivisionError: division by zero")
    assert parsed["level"] == "INFO"

def test_loggint(log):


    with pytest.raises(KeyError):
        log.critical(
            "hello",
            extra={"message": "abc", "msg": "test"}
        )
    


