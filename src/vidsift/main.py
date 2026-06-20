"""
Main file of vidsift

Tasks:
- parse CLI flags
- load config
- call one orchestrator (vidsift_pipeline.py)

"""
import logging

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
    def __init__(self) -> None:
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
        # setup bootstrap logging
        setup_bootstrap_logging()
        logger = logging.getLogger(__name__)

        # parse CLI flags
        args = parse_args()
        # load config.toml

        try:
            # load config.toml
            if args.config:
                config = load_config(
                    config_path=args.config
                )
            else:
                config = load_config()
        except InvalidConfigError as e:
            logger.exception(f"InvalidConfigError: {str(e)}")
            exit(1)
        except ConfigFileNotFoundError as e:
            logger.exception(f"ConfigFileNotFoundError: {str(e)}")
            exit(1)
        except ConfigFilePermissionError as e:
            logger.exception(f"ConfigFilePermissionError: {str(e)}")
            exit(1)
        except ConfigValidationError as e:
            logger.exception(f"ConfigValidationError: {str(e)}")
            exit(1)
        except ConfigError as e:
            logger.exception(f"ConfigError: {str(e)}")
            exit(1)

        # config override applying + validate it
        if args.loglevel is not None:
            console_config = config.logging.console.model_copy(
                update={"level": args.loglevel}
            )

            logging_config = config.logging.model_copy(
                update={"console": console_config}
            )

            config = config.model_copy(
                update={"logging": logging_config}
            )

        if args.global_ai_model is not None:
            ai_config = config.ai.model_copy(
                update={
                    "default_model": args.global_ai_model,
                    "validation_model": args.global_ai_model,
                    "summary_model": args.global_ai_model
                }
            )
            config = config.model_copy(
                update={"ai": ai_config}
            )

        self.config: AppConfig = config
        try:
            AppConfig.model_validate(self.config)
        except ValidationError as e:
            logger.exception(
                f"ConfigValidationError: Failed to load the config overrides into vidsift: {str(e)}",
            )
            exit(1)


        configure_logging(self.config)  # configure logger after app and logger config is loaded


        # execute args command
        if hasattr(args, "func"):
            try:
                args.func(args, config)
            except InvalidVideoError as e:
                logger.critical(
                    f"InvalidVideoError: Failed to create a video object to process videos: {str(e)}, exiting", exc_info=True,
                    extra={
                        "event": LogEvent.INVALID_VIDEO
                    }
                )
                exit(1)
            except SystemExit as e:
                logger.exception(
                    f"SystemExit: Vidsift got interrupted: {str(e)}",
                    extra={
                        "event": LogEvent.ORCHESTRATOR_INTERRUPTED,
                    }
                )
                exit(1)
            except KeyboardInterrupt as e:
                logger.exception(
                    f"KeyboardInterrupt: Vidsift go interrupted: {str(e)}",
                    extra={
                        "event": LogEvent.ORCHESTRATOR_INTERRUPTED
                    }
                )
                exit(130)
            else:
                logger.info(
                    "Orchestrator terminated successfully.",
                    extra={
                        "event": LogEvent.ORCHESTRATOR_STOPPED
                    }
                )
        else:
            logger.critical("No command provided, nothing to run")
            exit(1)


if __name__ == "__main__":
    vidsift_app: VidsiftCLI = VidsiftCLI()
    #vidsift_app.run()
