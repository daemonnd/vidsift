import json

from pydantic import ValidationError

from vidsift.config.parser import ConfigParser
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult

config_parser: ConfigParser = ConfigParser()

class MetadataValidator:
    def __init__(self) -> None:
        """
        raises:
        FileNotFoundError if validation prompt file not found
        PermissionError if validation prompt file does not have reading persimmsions
        """
        pass


