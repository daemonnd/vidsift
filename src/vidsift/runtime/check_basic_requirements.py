import logging
import os
from argparse import Namespace
from pathlib import Path


from vidsift.runtime.errors import BasicInitError
from vidsift.shared.paths import (
    VIDSIFT_DATA_DIR,
    VIDSIFT_LOG_DIR,
    VIDSIFT_CONFIG_FILE_PATH,
    VIDSIFT_CONFIG_PROMPTS_DIR,
)

logger = logging.getLogger(__name__)


class BasicInit:
    def __init__(self) -> None:
        pass

    def check_data_dir(self) -> None:
        if not VIDSIFT_DATA_DIR.exists():
            raise BasicInitError(
                f"The data dir of vidsift '{VIDSIFT_DATA_DIR}' does not exist."
            )
        if not VIDSIFT_DATA_DIR.is_dir():
            raise BasicInitError(
                f"The data dir of vidsift '{VIDSIFT_DATA_DIR}' is not a dir"
            )
        if not os.access(VIDSIFT_DATA_DIR, mode=os.R_OK):
            raise BasicInitError(
                f"Reading permissions for the vidsift data dir '{VIDSIFT_DATA_DIR}' are missing"
            )
        if not os.access(VIDSIFT_DATA_DIR, mode=os.W_OK):
            raise BasicInitError(
                f"Writing permissions for the vidsift data dir '{VIDSIFT_DATA_DIR}' are missing"
            )

    def check_config_dir(self) -> None:
        if self.args.config:
            config_file: Path = Path(self.args.config)
        else:
            config_file: Path = VIDSIFT_CONFIG_FILE_PATH

        if not config_file.exists():
            raise BasicInitError(f"The config file '{config_file}' does not exist")
        if not os.access(config_file, mode=os.R_OK):
            raise BasicInitError(
                f"Reading permissions for the vidsift config file '{config_file}' are missing"
            )

    def check_log_dir(self) -> None:
        if not VIDSIFT_LOG_DIR.exists():
            raise BasicInitError(
                f"The log dir of vidsift '{VIDSIFT_LOG_DIR}' does not exists"
            )
        if not VIDSIFT_LOG_DIR.is_dir():
            raise BasicInitError(
                f"The log dir of vidsift '{VIDSIFT_LOG_DIR}' is not a dir"
            )
        if not os.access(VIDSIFT_LOG_DIR, mode=os.W_OK):
            raise BasicInitError(
                f"Writing permissions for the vidsift log dir '{VIDSIFT_LOG_DIR}' are missing"
            )

    def check_prompts(self) -> None:

        if not VIDSIFT_CONFIG_PROMPTS_DIR.exists():
            raise BasicInitError(
                f"The prompt dir of vidsift '{VIDSIFT_CONFIG_PROMPTS_DIR}' does not exist"
            )

        if not VIDSIFT_CONFIG_PROMPTS_DIR.is_dir():
            raise BasicInitError(
                f"The prompt dir of vidsift '{VIDSIFT_CONFIG_PROMPTS_DIR}' is not a dir"
            )

        if not os.access(VIDSIFT_CONFIG_PROMPTS_DIR, mode=os.R_OK):
            raise BasicInitError(
                f"Reading permissions for the vidsift prompt dir '{VIDSIFT_CONFIG_PROMPTS_DIR}' are missing"
            )

        required_prompts: list[str] = [
            "chunk_summary.md",
            "full_summary.md",
            "metadata_retry.md",
            "metadata_validation.md",
            "transcript_retry.md",
            "transcript_validation.md",
        ]

        for prompt_name in required_prompts:
            prompt_file = VIDSIFT_CONFIG_PROMPTS_DIR / prompt_name

            if not prompt_file.exists():
                raise BasicInitError(
                    f"Required prompt file '{prompt_file}' does not exist"
                )

            if not prompt_file.is_file():
                raise BasicInitError(
                    f"Required prompt path '{prompt_file}' is not a file"
                )

            if not os.access(prompt_file, mode=os.R_OK):
                raise BasicInitError(
                    f"Reading permissions for the prompt file '{prompt_file}' are missing"
                )

    def check_files(self, args: Namespace) -> None:
        self.args = args
        self.check_data_dir()
        self.check_config_dir()
        self.check_prompts()
