"""
File to manage the locking, run starting etc.
"""
import logging
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid7

from platformdirs import user_log_dir

from vidsift.runtime.lock_manager import LockManager
from vidsift.shared.execution_context import (RunContext, reset_run_context,
                                              set_run_context)
from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)

class RunManager:
    def __init__(
        self, 
        lock_file_path: Path | None = None
    ) -> None:
        self.lock_file_path = lock_file_path
    def start_run(
            self,
            run_type: Literal["manual_pipeline_run", "manual_video_run", "schedule_run"],
            sleep_interval: float = 5,
    ):
        run_context = RunContext(run_id=uuid7())
        if self.lock_file_path:
            self.lock_manager: LockManager = LockManager(
                sleep_interval=sleep_interval,
                lock_file_path=self.lock_file_path
            )
        else:
            self.lock_manager: LockManager = LockManager(
                sleep_interval=sleep_interval
            )
        self.lock_manager.acquire(run_id=run_context.run_id)

        self.token = set_run_context(run_context)
        logger.info(
            "Acquired lock",
            extra={
                "event": LogEvent.LOCK_ACQUIRED,
            }
        )
        logger.info(
            "Run started",
            extra={
                "event": LogEvent.RUN_STARTED,
                "run_type": run_type,
                "log_file": f"{user_log_dir(appname='vidsift')}/vidsift.jsonl"            }
        )
        return self.token

    def end_run(self):
        try:
            logger.info(
                "Run completed",
                extra={
                    "event": LogEvent.RUN_COMPLETED,
                }
            )
            reset_run_context(self.token)
            self.lock_manager.release()
            logger.info(
                "Lock released",
                extra={
                    "event": LogEvent.LOCK_RELEASED,
                }
            )
        finally:
            #self.lock_manager.close()
            pass
