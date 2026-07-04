"""
File for managing the AI usage.
It runs the AI and generates the prompts for it
"""
from pathlib import Path

from vidsift.config.models import AppConfig


class PromptManager:
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


    def get_system_prompt(self) -> str:
        """
        Method to get the system prompt
        """
        return self.system_prompt
