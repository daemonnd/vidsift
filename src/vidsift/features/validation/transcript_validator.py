from pathlib import Path

from ollama import ChatResponse, chat

from vidsift.config.parser import VIDSIFT_CONFIG_DIR, ConfigParser
from vidsift.features.validation.errors import (EmptyAIResponseError,
                                                InvalidAIResponseFormatError,
                                                InvalidScoreError,
                                                VideoValidationError)
from vidsift.models.video import Video

config_parser: ConfigParser = ConfigParser()

class TranscriptValidator:
    def __init__(self, video: Video, model: str = "qwen3.6:27b") -> None:
        """
        raises:
        FileNotFoundError if validation prompt file not found
        PermissionError if validation prompt file does not have reading persimmsions
        """
        self.model=model
        self.video: Video = video
        self.validation_file: Path = Path(VIDSIFT_CONFIG_DIR / "prompts" / "transcript_validation.md")
        with open(self.validation_file, "r") as f:
            self.validation_system_prompt: str = f.read()

    def validate_video(self, transcript: str) -> str:
        response: ChatResponse = chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': self.generate_final_prompt(transcript=transcript),
            },
        ])
        if response.message.content is None:
            raise EmptyAIResponseError("The AI anwer is empty")
        return response.message.content

    """
    Function to validate the AI response, converting it to an integer between 0 and 100
    to have something to work with later when downloading/summarizing/doing nothing with the video
    """
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


    def generate_final_prompt(self, transcript: str) -> str:
        """
        Method to create a prompt out of the base prompt, the transcript and the custom instructions for that specific channel
        Returns the filnal prompt for the ai
        """
        return f"{transcript}{self.validation_system_prompt.replace("$CUSTOM_CHANNEL_INSTRUCTIONS", config_parser.get_custom_instructions(creator=self.video.author))}"






if __name__ == "__main__":
    with open(file="/home/user/projects/python/vidsift/fake-transcript.txt", mode="r") as file:
        transcript = file.read()
    video: Video = Video(
            title="sometitle",
            url="somelink",
            author="networkchuck",
            published="20206-345-3-45",
            video_id="some video id"
    )
