from pathlib import Path

from vidsift.features.validation.errors import CustomInstructionsReadingError


def get_custom_instructions(instructions_filename: str) -> str:
    """
    Method to get the custom per-channel instructions for validating a video from that channel id
    Returns the custom instructions.
    Raises:
    - FileNotFoundError if the path does not exist
    - PermissionError if the reading permissions are missing
    - exception if an unknown error occured
    """
    creator_instructions_path: Path = Path(Path().home() / ".config" / "vidsift" /"custom_channel_instructions")
    creator_instructions_path = creator_instructions_path / instructions_filename

    try:
        with open(file=Path(creator_instructions_path), mode="r") as f:
            return f.read()
    except FileNotFoundError as e:
        raise CustomInstructionsReadingError(str(e)) from e
    except PermissionError as e:
        raise CustomInstructionsReadingError(str(e)) from e
    except UnicodeDecodeError as e:
        raise CustomInstructionsReadingError(str(e)) from e


