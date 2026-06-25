"""
Main file of vidsift

Tasks:
- parse CLI flags
- load config
- call one orchestrator (vidsift_pipeline.py)

"""
import logging

from platformdirs import user_log_dir
from pydantic import ValidationError

from vidsift.cli.main import parse_args
from vidsift.config.errors import (ConfigError, ConfigFileNotFoundError,
                                   ConfigFilePermissionError,
                                   ConfigValidationError, InvalidConfigError)
from vidsift.config.loader import load_config
from vidsift.config.models import AppConfig
from vidsift.models.video import InvalidVideoError
from vidsift.shared.logging.bootstrap_logger import setup_bootstrap_logging
from vidsift.shared.logging.config import configure_logging
from vidsift.shared.logging.log_event_fields import LogEvent


class VidsiftCLI:
    """
    Manages vidsift bootstraping flow:
    1. setup bootstrap logging
    2. parse CLI flags
    3. load config.toml
    4. apply CLI overrides
    5. validate final config
    6. configure logging
    7. execute command
    """
    def __init__(self) -> None:
        # setup bootstrap logging
        setup_bootstrap_logging()
        self.logger = logging.getLogger(__name__)

        # parse CLI flags
        self.args = parse_args()
        # load config.toml

        try:
            # load config.toml
            if self.args.config:
                config = load_config(
                    config_path=self.args.config
                )
            else:
                config = load_config()
        except InvalidConfigError as e:
            self.logger.exception(f"InvalidConfigError: {str(e)}")
            exit(1)
        except ConfigFileNotFoundError as e:
            self.logger.exception(f"ConfigFileNotFoundError: {str(e)}")
            exit(1)
        except ConfigFilePermissionError as e:
            self.logger.exception(f"ConfigFilePermissionError: {str(e)}")
            exit(1)
        except ConfigValidationError as e:
            self.logger.exception(f"ConfigValidationError: {str(e)}")
            exit(1)
        except ConfigError as e:
            self.logger.exception(f"ConfigError: {str(e)}")
            exit(1)

        # config override applying + validate it
        if self.args.loglevel is not None:
            console_config = config.logging.console.model_copy(
                update={"level": self.args.loglevel}
            )

            logging_config = config.logging.model_copy(
                update={"console": console_config}
            )

            config = config.model_copy(
                update={"logging": logging_config}
            )

        if self.args.global_ai_model is not None:
            ai_config = config.ai.model_copy(
                update={
                    "default_model": self.args.global_ai_model,
                    "validation_model": self.args.global_ai_model,
                    "summary_model": self.args.global_ai_model
                }
            )
            config = config.model_copy(
                update={"ai": ai_config}
            )

        self.config: AppConfig = config
        try:
            AppConfig.model_validate(self.config)
        except ValidationError as e:
            self.logger.exception(
                f"ConfigValidationError: Failed to load the config overrides into vidsift: {str(e)}",
            )
            exit(1)


    def run(self) -> None:
        configure_logging(self.config)  # configure logger after app and logger config is loaded


        # execute args command
        if hasattr(self.args, "func"):
            try:
                self.args.func(self.args, self.config)
            except InvalidVideoError as e:
                self.logger.critical(
                    f"InvalidVideoError: Failed to create a video object to process videos: {str(e)}, exiting", exc_info=True,
                    extra={
                        "event": LogEvent.INVALID_VIDEO
                    }
                )
                exit(1)
            except KeyboardInterrupt as e:
                self.logger.exception(
                    f"KeyboardInterrupt: Vidsift go interrupted: {str(e)}",
                    extra={
                        "event": LogEvent.ORCHESTRATOR_INTERRUPTED
                    }
                )
                exit(130)
            else:
                self.logger.info(
                    "Orchestrator terminated successfully.",
                    extra={
                        "event": LogEvent.ORCHESTRATOR_STOPPED
                    }
                )
                exit(0)
        else:
            self.logger.critical("No command provided, nothing to run")
            exit(1)

def main() -> None:
    vidsift_app: VidsiftCLI = VidsiftCLI()
    vidsift_app.run()

if __name__ == "__main__":
    vidsift_app: VidsiftCLI = VidsiftCLI()
    vidsift_app.run()
