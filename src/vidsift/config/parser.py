"""
File to parse the config and transform the config into variables
"""
from pathlib import Path

from vidsift.shared.errorprotocol import logger

log = logger()

VIDSIFT_CONFIG_DIR: Path = Path(Path.home()/".config"/"vidsift")

MAX_ALLOWED_TITLE_CLICKBAIT_PHRASES: int = 2
MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_PHRASES: int = 10
MAX_ALLOWED_TITLE_CAPITAL_RATIO: float = 0.5
MAX_ALLOWED_TITLE_EMOJIS: int = 2


MAX_ALLOWED_TITLE_PUNCTUATION_RATIO: float = 0.07
MAX_ALLOWED_TITLE_UPPERCASE_RATIO: float = 0.4
MAX_ALLOWED_TITLE_EMOJI_RATIO: float = 0.15
MAX_ALLOWED_TITLE_CLICKBAIT_RATIO: float = 0.15
MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_RATIO: float = 0.1

WEAK_TITLE_UPPERCASE_RATIO: float = 0.2
WEAK_TITLE_EMOJI_RATIO: float = 0.03
WEAK_TITLE_PUNCTUATION_RATIO: float = 0.04
WEAK_TITLE_CLICKBAIT_RATIO: float = 0.05
WEAK_TRANSCRIPT_CLICKBAIT_RATIO: float = 0.02

WEIGHT_TITLE_UPPERCASE_RATIO: float = 1.0
WEIGHT_TITLE_EMOJI_RATIO: float = 1.0
WEIGHT_TITLE_PUNCTUATION_RATIO: float = 0.5
WEIGHT_TITLE_CLICKBAIT_RATIO: float = 1.5
WEIGHT_TRANSCRIPT_CLICKBAIT_RATIO: float = 2.5



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

        with open(file=Path(creator_instructions_path), mode="r") as f:
            return f.read()

if __name__ == "__main__":
    cp = ConfigParser()
    print(cp.get_custom_instructions("networkchuck"))
