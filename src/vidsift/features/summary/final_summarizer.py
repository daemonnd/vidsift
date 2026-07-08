from vidsift.config.models import AppConfig
from vidsift.models.ai_models import AIRequest
from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.executor import AIExecutor
from vidsift.shared.AI.prompt_manager import PromptManager


class FinalSummarizer:
    def __init__(self, config: AppConfig) -> None:
        """
            Raises: 
            - FileNotFoundError
            - PersmissionError
        """
        self.config: AppConfig = config
        self.prompt_manager: PromptManager = PromptManager(system_prompt_file_name="full_summary.md", config=self.config)
        self.ai_executor: AIExecutor = AIExecutor(config=config.ai)

    def summarize(self, summarized_chunks: list[str]) -> str:
        overall_summary_config = self.config.ai.tasks.overall_summary
        try:
            ai_request = AIRequest(
                prompt=self.prompt_manager.generate_prompt(append='\n'.join(summarized_chunks)),
                model=overall_summary_config.reference,
                max_tokens=overall_summary_config.max_tokens,
                context_length=overall_summary_config.context_length,
                thinking=overall_summary_config.thinking
            )
            return str(self.ai_executor.generate(request=ai_request).content)
        except AIError as e:
            raise AIError(f"An error occurred while summarizing the transcript: {str(e)}") from e


