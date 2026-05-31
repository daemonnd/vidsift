import json

from pydantic import ValidationError

from vidsift.config.parser import ConfigParser
from vidsift.features.validation.errors import InvalidAIResponseFormatError
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult

config_parser: ConfigParser = ConfigParser()

class MetadataValidator:
    def __init__(self, model: str) -> None:
        """
        raises:
        FileNotFoundError if validation prompt file not found
        PermissionError if validation prompt file does not have reading persimmsions
        """
        self.model=model


    def validate_ai_response(self, ai_response: str) -> MetadataValidationResult:
        """
        Method to validate the response of the AI.
        That includes:
        - checking wether the JSON is parsable
        - checking wether the values in the JSON have the correct type
        Raises:
        InvalidAIResponseFormatError if JSON is invalid or JSON output structure is broken
        """

        try:
            parsed_json = json.loads(ai_response)
            print(f"parsed json: {parsed_json}")
            validate_response = MetadataValidationResult.model_validate(parsed_json)
            print("model json schema")
            print(MetadataValidationResult.model_json_schema())
            return validate_response
        except json.JSONDecodeError as e:
            raise InvalidAIResponseFormatError(f"AI output invalid, invalid JSON syntax: {str(e)}")
        except ValidationError as e:
            raise InvalidAIResponseFormatError(f"Wrong JSON output structure: {str(e)}")



