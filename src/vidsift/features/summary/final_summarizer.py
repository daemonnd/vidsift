from vidsift.config.models import AppConfig
from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.run_model import AIUsageManager


class FinalSummarizer:
    def __init__(self, ai_model: str, config: AppConfig) -> None:
        """
            Raises: 
            - FileNotFoundError
            - PersmissionError
        """
        self.config: AppConfig = config
        self.ai_manager: AIUsageManager = AIUsageManager(system_prompt_file_name="full_summary.md", config=self.config)
        self.ai_model: str = ai_model

    def summarize(self, summarized_chunks: list[str]) -> str:
        try:
            return self.ai_manager.run_ai(self.ai_manager.generate_prompt(append='\n'.join(summarized_chunks)), model=self.ai_model)
        except AIError as e:
            raise AIError(f"An error occurred while summarizing the transcript: {str(e)}") from e


