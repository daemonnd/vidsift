import logging
from contextvars import Token
from time import sleep

from vidsift.config.models import AppConfig
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.runtime.errors import LockingError
from vidsift.shared.execution_context import reset_run_context
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.run_manager import RunManager

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
        self.locking_interval = locking_interval

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
        token: None | Token = None
        try:
            while True:
                run_manager = RunManager()
                token = run_manager.start_run(sleep_interval=self.locking_interval, run_type="schedule_run")
                try:
                    self.orchestrator.run()
                except SystemExit as e:
                    logger.info(
                        f"Orchestrator terminated: {str(e)}",
                        extra={
                            "event": LogEvent.ORCHESTRATOR_STOPPED,
                        }
                    )
                run_manager.end_run()
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
            if token:
                reset_run_context(token)

