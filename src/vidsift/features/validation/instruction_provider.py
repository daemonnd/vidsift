from pathlib import Path


def get_custom_instructions(creator: str) -> str:
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

