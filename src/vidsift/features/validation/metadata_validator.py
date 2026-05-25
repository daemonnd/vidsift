import json
from datetime import time
from pathlib import Path

from ollama import ChatResponse, chat
from pydantic import ValidationError

from vidsift.config.parser import VIDSIFT_CONFIG_DIR, ConfigParser
from vidsift.features.validation.errors import (EmptyAIResponseError,
                                                InvalidAIResponseFormatError)
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.video import Video
from vidsift.shared.ai_runner import AIUsageManager

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



if __name__ == "__main__":
    mv = MetadataValidator("qwen3.5:9b")
    vid: Video = Video(
        title="test",
        url="https",
        author="NetworkChuck",
        published="alsdjl",
        video_id="asldjfld"
    )
    ai_response = mv.validate_metadata(vid=vid)
    print("validation result")
    print(mv.validate_ai_response(ai_response=ai_response))
    print(f"the ai response is \n{mv.validate_metadata(vid=vid)}")
