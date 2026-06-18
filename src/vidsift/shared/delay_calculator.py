import logging
from random import randint
from time import sleep

from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)

def calculate_delay(min_delay: int, random_delay: int) -> int:
    return min_delay + randint(0, random_delay)

def sleep_delay(delay):
    logger.info(
        f"Sleeping {delay} seconds...",
        extra={
            "event": LogEvent.VIDEO_DELAY_STARTED,
            "delay": delay
        }
    )
    sleep(delay)
    logger.info(
        f"Finished sleeping {delay} seconds.",
        extra={
            "event": LogEvent.VIDEO_DELAY_COMPLETED
        }
    )
