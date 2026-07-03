"""
File for managing the AI usage.
It runs the AI and generates the prompts for it
"""
from pathlib import Path

from ollama import ChatResponse, Client, RequestError, ResponseError

from vidsift.config.models import AppConfig
from vidsift.shared.AI.errors import (AIModelError, AIRequestError,
                                      EmptyAIResponseError)


class AIUsageManager:
    def __init__(self, system_prompt_file_name: str, config: AppConfig) -> None:
        self.config: AppConfig = config
        self.sys_prompt_file: Path = Path(Path().home() / ".config" / "vidsift" / "prompts" / system_prompt_file_name)
        if not system_prompt_file_name:
            self.system_prompt: str = ""
        else:
            with open(self.sys_prompt_file, "r") as f:
                self.system_prompt: str = f.read()


    def generate_prompt(self,
                        system_prompt: str = "",
                        pattern: str = "",
                        replacement: str = "",
                        prepend: str = "",
                        append: str = "",
                        ) -> str:
        """
        Method to generate a prompt out of the given system prompt, and the parameters
        """
        # get the system prompt
        if not system_prompt:
            sys_prompt: str = self.system_prompt
        else:
            sys_prompt: str = system_prompt

        # replace pattern with replacement
        if pattern:
            prompt: str = sys_prompt.replace(pattern, replacement)
        else:
            prompt: str = sys_prompt

        # return with append and prepend
        return f"{prepend}{prompt}{append}"

    def run_ai(self, prompt: str, model: str) -> str:
        """
        Method to run the AI
        Raises:
        - EmptyAIResponseError if the AI response is empty
        - AIModelError if an error with the model occured
        """
        try:
            response: ChatResponse = Client(host=self.config.ai.host).chat(model=model,  messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            if not response.message.content:
                raise EmptyAIResponseError("The AI anwer is empty")
            if response.message.content.replace(" ", "") == "":
                raise EmptyAIResponseError("The AI anwer is empty")
            return response.message.content
        except ResponseError as e:
            raise AIModelError(f"An error occurred while running the AI model: {e}") from e
        except RequestError as e:
            raise AIRequestError(f"An error occured while making a request to the AI: {e}") from e

    def get_system_prompt(self) -> str:
        """
        Method to get the system prompt
        """
        return self.system_prompt
