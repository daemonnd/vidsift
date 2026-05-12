"""
File to parse the config and transform the config into variables
"""
from os import read
from pathlib import Path

from errorprotocol import logger

log = logger()

VIDSIFT_CONFIG_DIR: Path = Path(Path.home()/".config"/"vidsift")

class ConfigParser:
    def __init__(self) -> None:
        pass

    def get_custom_instructions(self, creator: str) -> str:
        """
        Method to get the custom per-channel instructions for validating a video from that creator
        Returns the custom instructions.
        """
        custom_instructions_path: Path = Path(VIDSIFT_CONFIG_DIR/"custom_channel_instructions")

        try:
            with open(file=Path(custom_instructions_path/f"{creator}.md"), mode="r") as f:
                return f.read()
        except FileNotFoundError as e:
            log.log_warning(f"FileNotFoundError: It seems that the path {str(Path(custom_instructions_path/f"{creator}.md"))} does not exist. The default custom instructions for {creator} will be used: {e}")
            return ""
        except PermissionError as e:
            log.log_warning(f"PermissionError: It seems that the path {str(Path(custom_instructions_path/f"{creator}.md"))} can't be read, reading permissions are missing: {e}")
            return ""

if __name__ == "__main__":
    cp = ConfigParser()
    print(cp.get_custom_instructions("networkchuck"))
