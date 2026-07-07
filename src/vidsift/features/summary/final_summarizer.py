from vidsift.config.models import AppConfig
from vidsift.models.ai_models import AIRequest
from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.executor import AIExecutor
from vidsift.shared.AI.prompt_manager import PromptManager


class FinalSummarizer:
    def __init__(self, ai_model: str, config: AppConfig) -> None:
        """
            Raises: 
            - FileNotFoundError
            - PersmissionError
        """
        self.config: AppConfig = config
        self.prompt_manager: PromptManager = PromptManager(system_prompt_file_name="full_summary.md", config=self.config)
        self.ai_model: str = ai_model
        self.ai_executor: AIExecutor = AIExecutor(config=config.ai)

    def summarize(self, summarized_chunks: list[str]) -> str:
        try:
            ai_request = AIRequest(
                prompt=self.prompt_manager.generate_prompt(append='\n'.join(summarized_chunks)),
                model=self.ai_model,
                max_tokens=1000,
                context_length=self.config.ai.summary_model_context_length,
                thinking=self.config.ai.overall_summary_think
            )
            return str(self.ai_executor.generate(request=ai_request).content)
        except AIError as e:
            raise AIError(f"An error occurred while summarizing the transcript: {str(e)}") from e


