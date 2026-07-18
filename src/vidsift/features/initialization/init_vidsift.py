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
    def copy_prompts(self) -> None:
        prompts_dir = resources.files("vidsift").joinpath("defaults/system_prompts")
        destination = Path(user_config_dir("vidsift")) / "system_prompts"

        for prompt in (
            "chunk_summary.md",
            "full_summary.md",
            "metadata_retry.md",
            "metadata_validation.md",
            "transcript_retry.md",
            "transcript_validation.md",
        ):
            with resources.as_file(prompts_dir.joinpath(prompt)) as src:
                shutil.copy(src=src, dst=destination)
    def create_necessary_dirs(self):
        (Path(user_config_dir("vidsift")) / "system_prompts").mkdir(parents=True, exist_ok=True) # also creates config dir cause parents
        Path(user_data_dir("vidsift")).mkdir(parents=True, exist_ok=True)
        Path(user_log_dir("vidsift")).mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        self.create_necessary_dirs()

        if self.force:
            self.copy_config()
            self.copy_prompts()
            return

        config_file = Path(user_config_dir("vidsift")) / "config.toml"
        if not config_file.exists():
            self.copy_config()

        prompts_dir = Path(user_config_dir("vidsift")) / "system_prompts"

        for prompt in (
            "chunk_summary.md",
            "full_summary.md",
            "metadata_retry.md",
            "metadata_validation.md",
            "transcript_retry.md",
            "transcript_validation.md",
        ):
            if not (prompts_dir / prompt).exists():
                with resources.as_file(
                    resources.files("vidsift").joinpath(f"defaults/system_prompts/{prompt}")
                ) as src:
                    shutil.copy(src=src, dst=prompts_dir)
