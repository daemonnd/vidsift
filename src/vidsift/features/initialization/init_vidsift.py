import importlib.resources as resources
import shutil
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir, user_log_dir


class InitVidsift:
    def __init__(self, force: bool) -> None:
        self.force: bool = force
    def copy_config(self):
        with resources.as_file(resources.files("vidsift").joinpath("defaults/config.toml")) as path:
            shutil.copy(
                src=path,
                dst=user_config_dir("vidsift")
            )
    def create_necessary_dirs(self):
        Path(user_config_dir("vidsift")).mkdir(parents=True, exist_ok=True)
        Path(user_data_dir("vidsift")).mkdir(parents=True, exist_ok=True)
        Path(user_log_dir("vidsift")).mkdir(parents=True, exist_ok=True)

    def initialize(self):
        self.create_necessary_dirs()
        if self.force:
            self.copy_config()
        if not (Path(user_config_dir("vidsift")) / "config.toml").exists():
            self.copy_config()


