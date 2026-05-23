from pathlib import Path

from ollama import ChatResponse, chat

from vidsift.config.parser import VIDSIFT_CONFIG_DIR
from vidsift.features.validation.errors import EmptyAIResponseError
from vidsift.models.video import Video


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


    def generate_final_prompt(self, vid: Video) -> str:
        """
        Method to get the final prompt send to the AI, containing both the metadata and the system prompt
        """
        return f"{vid}\n{self.validation_system_prompt}"
