from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.run_model import AIUsageManager


class Summarizer:
    def __init__(self, ai_model: str) -> None:
        """
            Raises: 
            - FileNotFoundError
            - PersmissionError
        """
        self.ai_manager: AIUsageManager = AIUsageManager(system_prompt_file_name="summary.md")
        self.ai_model: str = ai_model

    def summarize(self, transcript: str) -> str:
        try:
            return self.ai_manager.run_ai(self.ai_manager.generate_prompt(append=transcript), model=self.ai_model)
        except AIError as e:
            raise AIError(f"An error occurred while summarizing the transcript: {str(e)}") from e




if __name__ == "__main__":
    with open(file="/home/user/projects/python/vidsift/fake-transcript.txt", mode="r") as file:
        transcript = file.read()

    s = Summarizer("qwen3.5:9b")
    print(s.summarize(transcript=transcript))
