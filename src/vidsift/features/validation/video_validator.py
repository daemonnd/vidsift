from pathlib import Path

from ollama import ChatResponse, chat

from vidsift.config.parser import VIDSIFT_CONFIG_DIR, ConfigParser
from vidsift.models.video import Video
from vidsift.shared.errorprotocol import logger

log = logger()
config_parser: ConfigParser = ConfigParser()

class VideoValidator:
    def __init__(self, video: Video, model: str = "qwen3.6:27b") -> None:
        self.model=model
        self.video: Video = video
        self.validation_file: Path = Path(VIDSIFT_CONFIG_DIR / "prompts" / "validation.md")
        try:
            with open(self.validation_file, "r") as f:
                self.validation_system_prompt: str = f.read()
        except FileNotFoundError:
            log.log_error(f"FileNotFoundError: The file at {str(self.validation_file)} does not exist, making video validation impossible")
            raise
        except PermissionError:
            log.log_error(f"PermissionError: The file at {str(self.validation_file)} is not allowed to be red, making video validation impossible")
            raise
        except Exception as e:
            log.log_error(f"Exception while reading {str(self.validation_file)}: {e}")
            raise

    def validate_video(self, transcript: str) -> str | None:
        response: ChatResponse = chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': self.generate_final_prompt(transcript=transcript),
            },
        ])
        return response.message.content

    """
    Function to validate the AI response, converting it to an integer between 0 and 100
    to have something to work with later when downloading/summarizing/doing nothing with the video
    """
    def validate_ai_response(self, ai_response: str | None) -> int | None:
        try:
            if ai_response is None:
                log.log_warning("Because the AI response was empty, this video will be skipped")
                return
            ai_response_clean: str = ai_response.replace(" ", "")
            ai_response_score: int = int(ai_response_clean)
        except ValueError:
            log.log_warning("Ai response for validating a video failed, because the ai did not return a number as a score")
            return
        except Exception as e:
            log.log_error(f"Exception while converting the ai response for validaing the transcript: {e}")
            return
 
        # if it is actually a number that can be converted to an integer
        if ai_response_score > 100 or ai_response_score < 0:
            log.log_warning(f"Ai response is {ai_response_score}, which is not between 0 and 100, therefore this video will be skipped")
            return
        log.log_debug("SUCCESS")
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
    vv = VideoValidator(video=video)
    log.log_info("Testing with response j")
    vv.validate_ai_response("j")
    log.log_info("testing with response 6")
    vv.validate_ai_response("6")
    log.log_info("testing with response 101")
    vv.validate_ai_response("101")
    log.log_info("testing with reponse -1")
    vv.validate_ai_response("-1")
    log.log_info("testing with response $")
    vv.validate_ai_response("$")
    log.log_info("testing with reponse 4.4")
    vv.validate_ai_response("4.4")
    log.log_info("testing with ai response None")
    vv.validate_ai_response(None)
    print("\n")
    print(vv.validate_video(transcript))
