import json
from pathlib import Path

from ollama import ChatResponse, chat
from pydantic import ValidationError

from vidsift.config.parser import VIDSIFT_CONFIG_DIR, ConfigParser
from vidsift.features.validation.errors import (EmptyAIResponseError,
                                                InvalidAIResponseFormatError,
                                                InvalidScoreError,
                                                VideoValidationError)
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.video import Video

config_parser: ConfigParser = ConfigParser()

class MetadataValidator:
    def __init__(self, model: str) -> None:
        """
        raises:
        FileNotFoundError if validation prompt file not found
        PermissionError if validation prompt file does not have reading persimmsions
        """
        self.model=model

        self.metadata_sys_prompt_file: Path = Path(VIDSIFT_CONFIG_DIR / "prompts" / "metadata_validation.md")
        with open(self.metadata_sys_prompt_file, "r") as f:
            self.validation_system_prompt: str = f.read()

        self.metadata_retry_prompt_file: Path = Path(VIDSIFT_CONFIG_DIR / "prompts" / "metadata_retry.md")
        with open(self.metadata_retry_prompt_file, "r") as f:
            self.retry_system_prompt: str = f.read()

    def validate_metadata(self, prompt: str) -> str:
        """
        Method to run the AI against metadata, returns a string of JSON if it works.
        Raises:
        - EmptyAIResponseError if the AI response is empty
        """
        response: ChatResponse = chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        if response.message.content is None:
            raise EmptyAIResponseError("The AI anwer is empty")
        return response.message.content

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

    def generate_first_prompt(self, vid: Video) -> str:
        """
        Method to get the final prompt send to the AI, containing both the metadata and the system prompt
        This method generates the prompt for the first try.
        """
        return f"""
            {self.validation_system_prompt.replace("$CUSTOM_CHANNEL_INSTRUCTIONS", config_parser.get_custom_instructions(creator=vid.author))}
            title: {vid.title}
            author: {vid.author}
            published: {vid.published}
            url: {vid.url}
            video ID: {vid.video_id}
            """

    def generate_retry_prompt(self, prev_ai_output: str, error_msg: str) -> str:
        """
        Method that instructs the AI to correct the JSONDecodeError or ValidationError that occured because of a previous failure
        """
        return f"""
                {self.retry_system_prompt.replace("$ERROR_MESSAGE", error_msg).replace("$PREVIOUS_AI_OUTPUT", prev_ai_output)}
                """

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
