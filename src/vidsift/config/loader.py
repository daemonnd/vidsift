"""
File to parse the config and transform the config into variables
"""
import tomllib
from pathlib import Path

from vidsift.config.errors import (ConfigFileNotFoundError,
                                   ConfigFilePermissionError)
from vidsift.shared.errorprotocol import logger

log = logger()

VIDSIFT_CONFIG_DIR: Path = Path(Path.home()/".config"/"vidsift")




class ConfigLoader:
    def __init__(self) -> None:
        self.config_file_path: Path = Path(VIDSIFT_CONFIG_DIR / "config.toml")
    def get_config(self) -> dict:
        """
        Method to get the configfile as a dict
        Raises:
        - ConfigFilePermissionError if PermissionError occurs
        - ConfigFileNotFoundError if FileNotFoundError occurs
        Returns:
        The dict of the config file
        """
        try:
            with open(file=self.config_file_path, mode="rb") as f:
                return tomllib.load(f)
        except FileNotFoundError as e:
            raise ConfigFileNotFoundError(f"The config file has not been found at {self.config_file_path}: {str(e)}") from e
        except PermissionError as e:
            raise ConfigFilePermissionError(f"Permission Error while opening the config file at {self.config_file_path}: {str(e)}") from e


