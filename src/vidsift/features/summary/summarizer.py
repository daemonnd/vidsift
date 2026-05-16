from pathlib import Path

from ollama import ChatResponse, chat

from vidsift.config.parser import VIDSIFT_CONFIG_DIR
from vidsift.shared.errorprotocol import logger

log = logger()

class Summarizer:
    def __init__(self, transcript: str) -> None:
        self.transcript: str = transcript
        self.model='qwen3.6:27b'
        self.summary_prompt_file: Path = Path(VIDSIFT_CONFIG_DIR / "prompts" / "summary.md")
        try:
            with open(self.summary_prompt_file, "r") as f:
                self.summary_system_prompt: str = f.read()
        except FileNotFoundError:
            log.log_error(f"FileNotFoundError: The file at {str(self.summary_prompt_file)} does not exist, making video summarization impossible")
            raise
        except PermissionError:
            log.log_error(f"PermissionError: The file at {str(self.summary_prompt_file)} is not allowed to be red, making video summarization impossible")
            raise
        except Exception as e:
            log.log_error(f"Exception while reading {str(self.summary_prompt_file)}: {e}")
            raise

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
