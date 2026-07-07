import logging
import os
from argparse import Namespace
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir, user_log_dir

from vidsift.runtime.errors import BasicInitError

logger = logging.getLogger(__name__)


class BasicInit:
    def __init__(self) -> None:
        pass
    def check_data_dir(self) -> None:
        vidsift_data_dir: Path = Path(user_data_dir("vidsift"))
        if not vidsift_data_dir.exists():
            raise BasicInitError(f"The data dir of vidsift '{vidsift_data_dir}' does not exist.")
        if not vidsift_data_dir.is_dir():
            raise BasicInitError(f"The data dir of vidsift '{vidsift_data_dir}' is not a dir")
        if not os.access(vidsift_data_dir, mode=os.R_OK):
            raise BasicInitError(f"Reading permissions for the vidsift data dir '{vidsift_data_dir}' are missing")
        if not os.access(vidsift_data_dir, mode=os.W_OK):
            raise BasicInitError(f"Writing permissions for the vidsift data dir '{vidsift_data_dir}' are missing")

    def check_config_dir(self) -> None:
        if self.args.config:
            config_file: Path = Path(self.args.config)
        else:
            config_file: Path = Path(user_config_dir("vidsift")) / "config.toml"

        if not config_file.exists():
            raise BasicInitError(f"The config file '{config_file}' does not exist")
        if not os.access(config_file, mode=os.R_OK):
            raise BasicInitError(f"Reading permissions for the vidsift config file '{config_file}' are missing")

    def check_log_dir(self) -> None:
        vidsift_log_dir: Path = Path(user_log_dir("vidsift"))
        if not vidsift_log_dir.exists():
            raise BasicInitError(f"The log dir of vidsift '{vidsift_log_dir}' does not exists")
        if not vidsift_log_dir.is_dir():
            raise BasicInitError(f"The log dir of vidsift '{vidsift_log_dir}' is not a dir")
        if not os.access(vidsift_log_dir, mode=os.W_OK):
            raise BasicInitError(f"Writing permissions for the vidsift log dir '{vidsift_log_dir}' are missing")



    def check_files(self, args: Namespace) -> None:
        self.args = args
        self.check_data_dir()
        self.check_config_dir()
