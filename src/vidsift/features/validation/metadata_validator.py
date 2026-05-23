from pathlib import Path

from vidsift.config.parser import VIDSIFT_CONFIG_DIR
from vidsift.models.video import Video


class MetadataValidator:
    def __init__(self, model: str = 'qwen3.5:9b') -> None:
        """
        raises:
        FileNotFoundError if validation prompt file not found
        PermissionError if validation prompt file does not have reading persimmsions
        """
        self.model=model

        self.metadata_sys_prompt_file: Path = Path(VIDSIFT_CONFIG_DIR / "prompts" / "metadata_validation.md")
        with open(self.metadata_sys_prompt_file, "r") as f:
            self.validation_system_prompt: str = f.read()
