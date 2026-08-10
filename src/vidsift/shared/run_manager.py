"""
File to manage the locking, run starting etc.
"""

import logging
from pathlib import Path
from typing import Literal
from uuid import UUID

from vidsift.runtime.lock_manager import LockManager
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.paths import VIDSIFT_LOG_FILE

logger = logging.getLogger(__name__)


class RunManager:
    def __init__(self,  run_id: UUID,lock_file_path: Path | None = None) -> None:
        self.lock_file_path = lock_file_path
        self.run_id = run_id

    def start_run(
        self,
        run_type: Literal["manual_pipeline_run", "manual_video_run", "schedule_run"],
        sleep_interval: float = 5,
    ):
        if self.lock_file_path:
            self.lock_manager: LockManager = LockManager(
                sleep_interval=sleep_interval, lock_file_path=self.lock_file_path
            )
        else:
            self.lock_manager: LockManager = LockManager(sleep_interval=sleep_interval)
            self.lock_manager.acquire(self.run_id)

        logger.info(
            "Acquired lock",
            extra={
                "event": LogEvent.LOCK_ACQUIRED,
            },
        )
        logger.info(
            "Run started",
            extra={
                "event": LogEvent.RUN_STARTED,
                "run_type": run_type,
            },
        )

    def end_run(self):
        try:
            logger.info(
                "Run completed",
                extra={
                    "event": LogEvent.RUN_COMPLETED,
                },
            )
            self.lock_manager.release()
            logger.info(
                "Lock released",
                extra={
                    "event": LogEvent.LOCK_RELEASED,
                },
            )
        finally:
            # self.lock_manager.close()
            pass
