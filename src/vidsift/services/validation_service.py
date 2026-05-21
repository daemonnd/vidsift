"""
File for managing the validation process and returning the score of the video
"""
from vidsift.config.parser import (MAX_ALLOWED_TITLE_CLICKBAIT_PHRASES,
                                   MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_PHRASES)
from vidsift.features.validation.pre_validation import PreValidator
from vidsift.models.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.shared.errorprotocol import logger

log: logger = logger()


class VideoValidator:
    def __init__(self) -> None:
        self.pre_validator: PreValidator = PreValidator()

    @log.log
    def pre_validate(self, vid: Video, transcript: str) -> bool:
        """
        Method to run the pre validator, without using AI
        returns True if the video does not seem to be clickbait, False if it is
        """
        if self.pre_validator.check_title(title=vid.title) > (len(vid.title) / 2):
            log.log_info(f"The video {vid.title} with id {vid.video_id} contains a lot of characters indicating clickbait in the title (capital letters, emojis), it will be skipped")
            log.log_debug(f"Number of capital letters and emojis is the title: {self.pre_validator.check_title(title=vid.title)}")
            return False
        title_clickbait_phrases, transcript_clickbait_phrases =  self.pre_validator.check_clickbait_phrases(title=vid.title, transcript=transcript)
        if title_clickbait_phrases > MAX_ALLOWED_TITLE_CLICKBAIT_PHRASES:
            log.log_info(f"The video {vid.title} with id {vid.video_id} contains {title_clickbait_phrases} which is more than the allowed amount {MAX_ALLOWED_TITLE_CLICKBAIT_PHRASES}, it will be skipped")
            return False
        if transcript_clickbait_phrases > MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_PHRASES:
            log.log_info(f"The video {vid.title} with id {vid.video_id} contains {transcript_clickbait_phrases} clickbait phrases in the transcript, which is more than the allowed amount of {MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_PHRASES}, it will be skipped")
            return False
        log.log_debug(f"The video contained {title_clickbait_phrases} title clickbait phrases and {transcript_clickbait_phrases} transcript clickbait phrases")
        return True
 


    def validate_video(self, vid: Video, transcript: str) -> ValidationResult:
        pass

if __name__ == "__main__":
    vv = VideoValidator()
    vid = Video(title="asdlj.", url="lasjdlas", author="lsjaflöjd", published="aaioueopr", video_id="sadkasdjfl")
    transcript = "trust me trust me trust me trust me trust me trust me trust me trust me trust me trust me trust me urgent"
    print(vv.pre_validate(vid, transcript))
