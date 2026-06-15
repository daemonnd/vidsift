"""
File to parse the config and transform the config into variables
"""
import tomllib
from pathlib import Path
from tomllib import TOMLDecodeError

from pydantic import ValidationError

from vidsift.config.errors import (ConfigFileNotFoundError,
                                   ConfigFilePermissionError,
                                   ConfigValidationError, InvalidConfigError)
from vidsift.config.models import AppConfig

CONFIG_FILE_PATH: Path = Path(Path.home() / ".config" / "vidsift" / "config.toml")


def load_config(config_path: Path = CONFIG_FILE_PATH) -> AppConfig:
    try:
        with open(config_path, mode="rb") as f:
            return AppConfig.model_validate(tomllib.load(f))
    except TOMLDecodeError as e:
        raise InvalidConfigError(f"Unable to decode TOML in {config_path}: {str(e)}") from e
    except FileNotFoundError as e:
        raise ConfigFileNotFoundError(f"The config file has not been found at {config_path}: {str(e)}") from e
    except PermissionError as e:
        raise ConfigFilePermissionError(f"Permission Error while opening the config file at {config_path}: {str(e)}") from e
    except ValidationError as e:
        raise ConfigValidationError(f"The Config seems to be wrong: {str(e)}") from e


