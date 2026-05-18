from pathlib import Path

from ollama import ChatResponse, chat

from vidsift.config.parser import VIDSIFT_CONFIG_DIR


class Summarizer:
    def __init__(self, transcript: str) -> None:
        """
            Raises: 
            - FileNotFoundError
            - PersmissionError
        """
        self.transcript: str = transcript
        self.model='qwen3.5:9'
        self.summary_prompt_file: Path = Path(VIDSIFT_CONFIG_DIR / "prompts" / "summary.md")
        with open(self.summary_prompt_file, "r") as f:
            self.summary_system_prompt: str = f.read()

    def summarize(self) -> str | None:

        response: ChatResponse = chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': f"{self.summary_system_prompt}\n{self.transcript}",
            },
        ])
        return response.message.content

if __name__ == "__main__":
    with open(file="/home/user/projects/python/vidsift/fake-transcript.txt", mode="r") as file:
        transcript = file.read()

    s = Summarizer(transcript=transcript)
    print(s.summarize())
