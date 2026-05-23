from pathlib import Path

from ollama import ChatResponse, chat

from vidsift.config.parser import VIDSIFT_CONFIG_DIR, ConfigParser
from vidsift.features.validation.errors import (EmptyAIResponseError,
                                                InvalidAIResponseFormatError,
                                                InvalidScoreError,
                                                VideoValidationError)
from vidsift.models.video import Video

config_parser: ConfigParser = ConfigParser()

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

    def validate_metadata(self, vid: Video) -> str:
        response: ChatResponse = chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': self.generate_final_prompt(vid=vid),
            },
        ])
        if response.message.content is None:
            raise EmptyAIResponseError("The AI anwer is empty")
        return response.message.content

    def validate_ai_response(self, ai_response: str) -> int:
        try:
            ai_response_score: int = int(ai_response)
        except ValueError:
            raise InvalidAIResponseFormatError(f"The AI output is {ai_response}, which is not a valid integer")
        except Exception as e:
            raise VideoValidationError(f"{e}")
 
        # if it is actually a number that can be converted to an integer
        if ai_response_score > 100 or ai_response_score < 0:
            raise InvalidScoreError(f"The AI response score is {ai_response_score}, which is not between 0 and 100")
        return ai_response_score

    def generate_final_prompt(self, vid: Video) -> str:
        """
        Method to get the final prompt send to the AI, containing both the metadata and the system prompt
        """
        return f"{self.validation_system_prompt.replace("$CUSTOM_CHANNEL_INSTRUCTIONS", config_parser.get_custom_instructions(creator=vid.author))}{vid}"

if __name__ == "__main__":
    mv = MetadataValidator()
    vid: Video = Video(
        title="test",
        url="https",
        author="NetworkChuck",
        published="alsdjl",
        video_id="asldjfld"
    )
    print(f"the ai response is \n{mv.validate_metadata(vid=vid)}")
