"""
Main file of vidsift

Tasks:
- parse CLI flags
- load config
- call one orchestrator (vidsift_pipeline.py)

"""
#import argparse

import logging

from vidsift.config.errors import (ConfigError, ConfigFileNotFoundError,
                                   ConfigFilePermissionError,
                                   ConfigValidationError, InvalidConfigError)
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.shared.logging.bootstrap_logger import setup_bootstrap_logging
from vidsift.shared.logging.config import configure_logging


class VidsiftCLI:
    def __init__(self) -> None:
        setup_bootstrap_logging()
        logger = logging.getLogger(__name__)
        try:
            from vidsift.config import \
                CONFIG  # make the config run after bootstrap logger setup
        except InvalidConfigError as e:
            logger.exception(f"InvalidConfigError: {str(e)}")
            exit(1)
        except ConfigFileNotFoundError as e:
            logger.exception(f"ConfigFileNotFoundError: {str(e)}")
            exit(1)
        except ConfigFilePermissionError as e:
            logger.exception(f"ConfigFilePermissionError: {str(e)}")
        except ConfigValidationError as e:
            logger.exception(f"ConfigValidationError: {str(e)}")
        except ConfigError as e:
            logger.exception(f"ConfigError: {str(e)}")
        configure_logging()  # configure logger after app and logger config is loaded
#        self.config_parser: ConfigParser = ConfigParser()
        self.orchestrator: VidsiftOrchestrator = VidsiftOrchestrator(["UCo71RUe6DX4w-Vd47rFLXPg"])
    def start_pipeline(self) -> None:
        self.orchestrator.run()


if __name__ == "__main__":
    vidsift_app: VidsiftCLI = VidsiftCLI()
    vidsift_app.start_pipeline()
