"""
File to manage the locking, run starting etc.
"""
import logging
from typing import Literal
from uuid import uuid7

from vidsift.runtime.lock_manager import LockManager
from vidsift.shared.execution_context import (RunContext, reset_run_context,
                                              set_run_context)
from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)

class RunManager:
    def start_run(
            self,
            owner: Literal["scheduler", "manual"],
            run_type: Literal["manual_pipeline_run", "manual_video_run", "schedule_run"],
            sleep_interval: float = 5
    ):
        self.owner: Literal["scheduler", "manual"] = owner
        self.lock_manager: LockManager = LockManager(owner=self.owner, sleep_interval=sleep_interval)
        self.lock_manager.acquire(self.owner)

        run_context = RunContext(run_id=uuid7())
        self.token = set_run_context(run_context)
        logger.info(
            "Acquired lock",
            extra={
                "event": LogEvent.LOCK_ACQUIRED,
                "owner": self.owner
            }
        )
        logger.info(
            "Run started",
            extra={
                "event": LogEvent.RUN_STARTED,
                "run_type": run_type
            }
        )
        return self.token

    def end_run(self):
            logger.info(
                "Run completed",
                extra={
                    "event": LogEvent.RUN_COMPLETED,
                    "owner": self.owner
                }
            )
            reset_run_context(self.token)
            self.lock_manager.release(self.owner)
            logger.info(
                "Lock released",
                extra={
                    "event": LogEvent.LOCK_RELEASED,
                    "owner": self.owner
                }
            )
