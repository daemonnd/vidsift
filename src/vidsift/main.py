"""
Main file of vidsift

Tasks:
- parse CLI flags
- load config
- call one orchestrator (vidsift_pipeline.py)

"""
import logging
from pathlib import Path
from uuid import uuid7

from pydantic import ValidationError

from vidsift.cli.main import parse_args
from vidsift.config.errors import (ConfigError, ConfigFileNotFoundError,
                                   ConfigFilePermissionError,
                                   ConfigValidationError, InvalidConfigError)
from vidsift.config.loader import load_config
from vidsift.config.models import AppConfig
from vidsift.features.initialization.init_vidsift import InitVidsift
from vidsift.models.video import InvalidVideoError
from vidsift.runtime.check_basic_requirements import BasicInit
from vidsift.runtime.errors import BasicInitError
from vidsift.shared.execution_context import (RunContext, reset_run_context,
                                              set_run_context)
from vidsift.shared.logging.bootstrap_logger import setup_bootstrap_logging
from vidsift.shared.logging.config import configure_logging
from vidsift.shared.logging.log_event_fields import LogEvent

PIPELINE_RUNNING_COMMANDS: list[str] = ["run", "schedule", "process"]


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
        self._bootstrap()
        self._initialize_application()

    def _bootstrap(self):
        # setup bootstrap logging
        setup_bootstrap_logging()
        self.logger = logging.getLogger(__name__)

        # parse CLI flags
        self.args = parse_args()

        # the args.command will not change with any cli overrides so it is safe to do this before applying the overrides
        self.run_context = RunContext(run_id=uuid7())
        self.run_token = set_run_context(self.run_context)
        # check wether command is init to repair basic requirements before exit
        if self.args.command == "init":
            vidsift_init: InitVidsift = InitVidsift(force=self.args.force)
            vidsift_init.initialize()
            self._exit(0)

        # check if basic requirements are there
        try:
            basic_init: BasicInit = BasicInit()
            basic_init.check_files(args=self.args)
        except BasicInitError as e:
            self.logger.exception(
                f"BasicInitError: {str(e)}. Run 'vidsift init' first to setup basic config and other files"
            )
            self._exit(1)

    def _load_config(self) -> AppConfig:
        # load config.toml
        try:
            # load config.toml
            if self.args.config:
                return load_config(config_path=self.args.config)
            else:
                return load_config()
        except InvalidConfigError as e:
            self.logger.exception(f"InvalidConfigError: {str(e)}")
            self._exit(1)
        except ConfigFileNotFoundError as e:
            self.logger.exception(f"ConfigFileNotFoundError: {str(e)}")
            self._exit(1)
        except ConfigFilePermissionError as e:
            self.logger.exception(f"ConfigFilePermissionError: {str(e)}")
            self._exit(1)
        except ConfigValidationError as e:
            self.logger.exception(f"ConfigValidationError: {str(e)}")
            self._exit(1)
        except ConfigError as e:
            self.logger.exception(f"ConfigError: {str(e)}")
            self._exit(1)

    def _apply_cli_overrides(self, config: AppConfig) -> AppConfig:
        """
        Method that takes the config from the config file, and returns the config with the cli overrides applied
        """
        if self.args.loglevel is not None:
            console_config = config.logging.console.model_copy(
                update={"level": self.args.loglevel}
            )

            logging_config = config.logging.model_copy(
                update={"console": console_config}
            )

            config = config.model_copy(update={"logging": logging_config})

        if self.args.global_ai_model is not None:
            metadata_validation = config.ai.tasks.metadata_validation.model_copy(
                update={"reference": self.args.global_ai_model}
            )

            transcript_validation = config.ai.tasks.transcript_validation.model_copy(
                update={"reference": self.args.global_ai_model}
            )

            chunk_summary = config.ai.tasks.chunk_summary.model_copy(
                update={"reference": self.args.global_ai_model}
            )

            overall_summary = config.ai.tasks.overall_summary.model_copy(
                update={"reference": self.args.global_ai_model}
            )

            tasks_config = config.ai.tasks.model_copy(
                update={
                    "metadata_validation": metadata_validation,
                    "transcript_validation": transcript_validation,
                    "chunk_summary": chunk_summary,
                    "overall_summary": overall_summary,
                }
            )

            ai_config = config.ai.model_copy(update={"tasks": tasks_config})

            config = config.model_copy(update={"ai": ai_config})

        if self.args.skip_ai_checks is True:
            ai_config = config.ai.model_copy(
                update={
                    "skip_ai_checks": self.args.skip_ai_checks,
                }
            )
            config = config.model_copy(update={"ai": ai_config})

        if self.args.debug is not None:

            def update_dependencies(config: AppConfig):
                console_logging_config = config.logging.console.model_copy(
                    update={"dependency_level": "DEBUG"}
                )
                logging_config = config.logging.model_copy(
                    update={"console": console_logging_config}
                )
                config = config.model_copy(update={"logging": logging_config})
                return config

            def update_yt_dlp(config: AppConfig):
                yt_dlp_base_config = config.video_processing.yt_dlp.base.model_copy(
                    update={"quiet": False}
                )
                yt_dlp_config = config.video_processing.yt_dlp.model_copy(
                    update={"base": yt_dlp_base_config}
                )
                video_processing_config = config.video_processing.model_copy(
                    update={"yt_dlp": yt_dlp_config}
                )
                config = config.model_copy(
                    update={"video_processing": video_processing_config}
                )
                return config

            match self.args.debug:
                case "dependencies":
                    config = update_dependencies(config)
                case "yt-dlp":
                    config = update_yt_dlp(config)
                case "all":
                    config = update_dependencies(config)
                    config = update_yt_dlp(config)
                    console_config = config.logging.console.model_copy(
                        update={"level": "DEBUG"}
                    )

                    logging_config = config.logging.model_copy(
                        update={"console": console_config}
                    )

                    config = config.model_copy(update={"logging": logging_config})

        if self.args.command == "run" or self.args.command == "schedule":
            if self.args.skip_interrupted is True:
                video_processing_config = config.video_processing.model_copy(
                    update={"skip_interrupted_vids": True}
                )

                config = config.model_copy(
                    update={"video_processing": video_processing_config}
                )
            if self.args.skip_new is True:
                video_processing_config = config.video_processing.model_copy(
                    update={"skip_new_vids": True}
                )
                config = config.model_copy(
                    update={"video_processing": video_processing_config}
                )

        if self.args.command in PIPELINE_RUNNING_COMMANDS:
            if self.args.fake_download is not None and self.args.fake_download is not True:
                video_download_config = config.downloads.model_copy(
                    update={
                        "fake_download": True,
                        "output_path": self.args.fake_download
                    }
                )
                config = config.model_copy(
                    update={"downloads": video_download_config}
                )
            elif self.args.fake_download is True:
                video_download_config = config.downloads.model_copy(
                    update={
                        "fake_download": True,
                    }
                )
                config = config.model_copy(
                    update={"downloads": video_download_config}
                )
        if config.downloads.output_path is None:
            video_download_config = config.downloads.model_copy(
                update={
                    "output_path": Path(config.downloads.output_dir) / "to_watch.md"
                }
            )
            config = config.model_copy(
                update={"downloads": video_download_config}
            )
        return config

    def _validate_config(self, config: AppConfig):
        """
        Method that validates the final config (it already got overridden by the args) and defines it as an attribute if it is valid
        """
        self.config: AppConfig = config
        try:
            AppConfig.model_validate(self.config)
        except ValidationError as e:
            self.logger.exception(
                f"ConfigValidationError: Failed to load the config overrides into vidsift: {str(e)}",
            )
            self._exit(1)

    def run(self) -> None:
        configure_logging(
            self.config
        )  # configure logger after app and logger config is loaded

        # log the loaded config to the file
        logger = logging.getLogger(__name__)
        logger.debug(
            "Starting new vidsift instance",
            extra={
                "event": LogEvent.CONFIG_LOADED,
                "file_only": True,
                "loaded_config": self.config.model_dump(),
                "cli_args": self.args,
            },
        )

        # execute args command
        if hasattr(self.args, "func"):
            try:
                self.args.func(self.args, self.config, self.run_context.run_id)
            except InvalidVideoError as e:
                self.logger.critical(
                    f"InvalidVideoError: Failed to create a video object to process videos: {str(e)}, exiting",
                    exc_info=True,
                    extra={"event": LogEvent.INVALID_VIDEO},
                )
                self._exit(1)
            except KeyboardInterrupt:
                self.logger.exception(
                    "Exiting due to KeyboardInterrupt.",
                    extra={"event": LogEvent.ORCHESTRATOR_INTERRUPTED},
                )
                self._exit(130)
            else:
                if self.args.command in PIPELINE_RUNNING_COMMANDS:
                    self.logger.info(
                        "Orchestrator terminated successfully.",
                        extra={"event": LogEvent.ORCHESTRATOR_STOPPED},
                    )
                self._exit(0)
        else:
            self.logger.critical("No command provided, nothing to run")
            self._exit(1)

    def _initialize_application(self) -> None:
        config = self._load_config()
        config = self._apply_cli_overrides(config=config)
        self._validate_config(config=config)

    def _exit(self, code: int):
        reset_run_context(self.run_token)
        exit(code)


def main() -> None:
    vidsift_app: VidsiftCLI = VidsiftCLI()
    vidsift_app.run()


if __name__ == "__main__":
    vidsift_app: VidsiftCLI = VidsiftCLI()
    vidsift_app.run()
