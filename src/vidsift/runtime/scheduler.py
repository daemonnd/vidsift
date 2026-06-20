import logging
from time import sleep

from vidsift.config.models import AppConfig
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.runtime.errors import LockingError
from vidsift.runtime.lock_manager import LockManager
from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)

class BackgroundServiceManager:
    def __init__(
            self,
        orchestrator: VidsiftOrchestrator,
        config: AppConfig,
        locking_interval: float = 10
    ) -> None:
        self.orchestrator: VidsiftOrchestrator = orchestrator
        self.config: AppConfig = config
        self.lock_manager: LockManager = LockManager(
            owner="scheduler",
            sleep_interval=locking_interval
        )

    def run(
        self,
        sleep_interval: int = 1800
    ) -> None:
        """
        What it does:
        1. aquire lock
        2. run the vidsift pipeline
        3. after that, free the lock
        4. sleep sleep_interval seconds
        repeat
        """
        try:
            while True:
                self.lock_manager.acquire(owner="scheduler")
                logger.info(
                    "Acquired lock",
                    extra={
                        "event": LogEvent.LOCK_ACQUIRED
                    }
                )
                try:
                    self.orchestrator.run()
                except SystemExit as e:
                    logger.info(
                        f"Orchestrator terminated: {str(e)}",
                        extra={
                            "event": LogEvent.ORCHESTRATOR_STOPPED,
                        }
                    )
                self.lock_manager.release(owner="scheduler")
                logger.info(
                    "Lock released",
                    extra={
                        "event": LogEvent.LOCK_RELEASED
                    }
                )
                logger.info(
                    "Scheduler cooldown started",
                    extra={
                        "event": LogEvent.SCHEDULER_COOLDOWN_STARTED,
                        "interval": sleep_interval
                    }
                )
                sleep(sleep_interval)
                logger.info(
                    "Scheduler cooldown completed",
                    extra={
                        "event": LogEvent.SCHEDULER_COOLDOWN_COMPLETED,
                        "interval": sleep_interval
                    }
                )

        except LockingError as e:
            logger.exception(
                f"LockingError: {str(e)}",
                extra={
                    "event": LogEvent.LOCK_FAILED,
                }
            )
        finally:
            self.lock_manager.release(owner="scheduler")
