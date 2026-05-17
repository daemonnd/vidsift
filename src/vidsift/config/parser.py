"""
File to parse the config and transform the config into variables
"""
from pathlib import Path

from vidsift.shared.errorprotocol import logger

log = logger()

VIDSIFT_CONFIG_DIR: Path = Path(Path.home()/".config"/"vidsift")

class ConfigParser:
    def __init__(self) -> None:
        pass

    def get_custom_instructions(self, creator: str) -> str:
        """
        Method to get the custom per-channel instructions for validating a video from that creator
        Returns the custom instructions.
        Raises:
        - FileNotFoundError if the path does not exist
        - PermissionError if the reading permissions are missing
        - exception if an unknown error occured
        """
        custom_instructions_path: Path = Path(VIDSIFT_CONFIG_DIR/"custom_channel_instructions")
        creator_instructions_path:Path = Path(custom_instructions_path/f"{creator}.md")

        try:
            with open(file=Path(custom_instructions_path/f"{creator}.md"), mode="r") as f:
                return f.read()
        except FileNotFoundError as e:
            log.log_warning(f"FileNotFoundError: It seems that the path {str(creator_instructions_path)} does not exist. The default custom instructions for {creator} will be used: {e}")
            raise FileNotFoundError(f"It seems that the path {str(creator_instructions_path)} does not exist. The default custom instructions for {creator} will be used: {e}")        
        except PermissionError as e:
            log.log_warning(f"PermissionError: It seems that the path {str(creator_instructions_path)} can't be read, reading permissions are missing: {e}")
            raise PermissionError(f"It seems that the path {str(creator_instructions_path)} can't be read, reading permissions are missing: {e}")
        except Exception as e:
            log.log_warning(f"Exception occured while trying to open {str(creator_instructions_path)}: {e}")
            raise Exception(str(e))

if __name__ == "__main__":
    cp = ConfigParser()
    print(cp.get_custom_instructions("networkchuck"))
