from ollama import ChatResponse, chat

from config_parser import ConfigParser
from errorprotocol import logger
from video_data import Video

log = logger()
config_parser: ConfigParser = ConfigParser()

class VideoValidator:
    def __init__(self, video: Video, model: str = "qwen3.6:27b") -> None:
        self.model=model
        self.video: Video = video
        self.message="""
# IDENTITY and PURPOSE

You are an ultra-wise and brilliant classifier and judge of content. You rate youtube transcripts from 0 (bad) to 100 (excellent) based on content, ideas and tension.

Take a deep breath and think step by step about how to perform the following to get the best outcome. You have a lot of freedom to do this the way you think is best.

# STEPS

- Understand the transcript deeply. Think about things like: `Is that a good video?` `Is that one worth the time of the user?`  while reading.

- Rate the content based on the number of ideas in the input (0-40: bad 40-80: good 80-100: excellent) combined with how well it matches this:

# How you should score this video

$CUSTOM_CHANNEL_INSTRUCTIONS

---

## Use the following rating levels

- Provide a score between 1 and 100 for the overall quality ranking, where 100 is a perfect match with the highest number of high quality ideas, and 1 is the worst match with a low number of the worst ideas.

## Context

- The ranking will be used in a script that checks your output. If the score is ... then ...
 	- 0-40; then the video will be skipped
 	- 41-80; then the video gets summarized for the user
 	- 81-100; then the video gets downloaded for the user
But your task is to ONLY provide the ranking. That is just so that you know what the ranking means in more detail.

## OUTPUT INSTRUCTIONS

1. You only output the rating (an integer between 0 and 100), NOTHING ELSE!!!. That means: no "40"
LITERALLY the number, THAT's it!!!
 That means: Only literally output the score.

2. Do not give warnings or notes; only output the requested section.
"""
    def validate_video(self, transcript: str) -> str | None:
        response: ChatResponse = chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': self.generate_final_prompt(transcript=transcript),
            },
        ])
        return response.message.content

    """
    Function to validate the ai response, converting it to an integer between 0 and 100
    to have something to work with later when downloading/summarizing/doing nothing with the video
    """
    def validate_ai_response(self, ai_response: str | None) -> int | None:
        try:
            if ai_response is None:
                log.log_warning("Because the AI response was empty, this video will be skipped")
                return
            ai_response_score: int = int(ai_response)
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
        return f"{self.message.replace("$CUSTOM_CHANNEL_INSTRUCTIONS", config_parser.get_custom_instructions(creator=self.video.author))}{transcript}"






if __name__ == "__main__":
    with open(file="/home/user/projects/python/vidsift/fake-transcript.txt", mode="r") as file:
        transcript = file.read()
    video: Video = Video(
            title="sometitle",
            link="somelink",
            author="networkchuck",
            published="20206-345-3-45"
    )
    vv = VideoValidator(video=video)
    print(vv.generate_final_prompt(transcript=transcript))
    exit(1)
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
