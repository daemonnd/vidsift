import importlib.resources as resources
import shutil
from pathlib import Path
from vidsift.shared.paths import (
    VIDSIFT_CONFIG_PROMPTS_DIR,
    VIDSIFT_CONFIG_FILE_PATH,
    VIDSIFT_CONFIG_DIR,
    VIDSIFT_LOG_DIR,
    VIDSIFT_DATA_DIR,
)


class InitVidsift:
    def __init__(self, force: bool) -> None:
        self.force: bool = force

    def copy_config(self):
        with resources.as_file(
            resources.files("vidsift").joinpath("defaults/config.toml")
        ) as path:
            shutil.copy(src=path, dst=VIDSIFT_CONFIG_DIR)

    def copy_prompts(self) -> None:
        prompts_dir = resources.files("vidsift").joinpath("defaults/system_prompts")
        destination: Path = VIDSIFT_CONFIG_PROMPTS_DIR

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
        VIDSIFT_CONFIG_PROMPTS_DIR.mkdir(
            parents=True, exist_ok=True
        )  # also creates config dir cause parents
        VIDSIFT_DATA_DIR.mkdir(parents=True, exist_ok=True)
        VIDSIFT_LOG_DIR.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        self.create_necessary_dirs()

        if self.force:
            self.copy_config()
            self.copy_prompts()
            return

        config_file = VIDSIFT_CONFIG_FILE_PATH
        if not config_file.exists():
            self.copy_config()

        for prompt in (
            "chunk_summary.md",
            "full_summary.md",
            "metadata_retry.md",
            "metadata_validation.md",
            "transcript_retry.md",
            "transcript_validation.md",
        ):
            if not (VIDSIFT_CONFIG_PROMPTS_DIR / prompt).exists():
                with resources.as_file(
                    resources.files("vidsift").joinpath(
                        f"defaults/system_prompts/{prompt}"
                    )
                ) as src:
                    shutil.copy(src=src, dst=prompts_dir)
