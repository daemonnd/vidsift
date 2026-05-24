"""
File for managing the validation process and returning the score of the video
"""
from dataclasses import asdict
from pprint import pprint

from vidsift.config.parser import (MAX_ALLOWED_TITLE_CAPITAL_RATIO,
                                   MAX_ALLOWED_TITLE_CLICKBAIT_PHRASES,
                                   MAX_ALLOWED_TITLE_EMOJIS,
                                   MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_PHRASES)
from vidsift.features.validation.errors import (EmptyAIResponseError,
                                                InvalidAIResponseFormatError)
from vidsift.features.validation.metadata_validator import MetadataValidator
from vidsift.features.validation.pre_validation import PreValidator
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.validation.pre_validation_result import PreValidationResult
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.shared.errorprotocol import logger
from vidsift.shared.text_normalizer import TextNormalizer

log: logger = logger()


class VideoValidator:
    def __init__(self, ai_model: str = "qwen3.5:9b") -> None:
        self.pre_validator: PreValidator = PreValidator()
        self.text_normalizer: TextNormalizer = TextNormalizer()
        self.metadata_validator: MetadataValidator = MetadataValidator(model=ai_model)

    @log.log
    def pre_validate(self, vid: Video, raw_transcript: str) -> PreValidationResult:
        """
        Method to run the pre validator, without using AI
        returns True if the video does not seem to be clickbait, False if it is
        """
        title: str = self.text_normalizer.normalize(vid.title)
        transcript: str = self.text_normalizer.normalize(raw_transcript)

        # title char length
        title_char_length: int = len(title)

        # title uppercase ratio
        title_uppercase_chars: int = self.pre_validator.check_title_uppercase(title=title)
        title_uppercase_ratio: float = (max(title_char_length, 1) * max(title_uppercase_chars, 1)) / 100 # to get the number in %

        # title emoji count and list
        title_emoji_count, title_emoji_list = self.pre_validator.get_emoji_count(title=title)

        # clickbait patterns
        title_clickbait_patterns, transcript_clickbait_patterns = self.pre_validator.check_clickbait_phrases(title=title, transcript=transcript)

        return PreValidationResult(
            title_emoji_count=title_emoji_count,
            title_emoji_list=title_emoji_list,
            title_char_length=title_char_length,
            title_uppercase_ratio=title_uppercase_ratio,
            title_clickbait_patters=title_clickbait_patterns,
            transcript_clickbait_patterns=transcript_clickbait_patterns
        )

    def get_pre_validate_hard_stop(self, pre_validation_result: PreValidationResult, vid: Video) -> bool:
        """
        Method to check wether the current video should be skipped or not
        Returns True if there should be a hard stop and False if not
        """
        if pre_validation_result.title_char_length == 0:
            log.log_info(f"Skipping Video with id {vid.video_id} because title char length is 0")
            return True
        if pre_validation_result.title_uppercase_ratio > MAX_ALLOWED_TITLE_CAPITAL_RATIO:
            log.log_info(f"Skipping Video with id {vid.video_id} because max allowed capital letter ratio in title {MAX_ALLOWED_TITLE_CAPITAL_RATIO} is exeeded with {pre_validation_result.title_uppercase_ratio}")
            return True
        if pre_validation_result.title_clickbait_patters > MAX_ALLOWED_TITLE_CLICKBAIT_PHRASES:
            log.log_info(f"Skipping Video with id {vid.video_id} because max allowed clickbait phrases in title {MAX_ALLOWED_TITLE_CLICKBAIT_PHRASES} is exeeded with {pre_validation_result.title_clickbait_patters}")
            return True
        if pre_validation_result.transcript_clickbait_patterns > MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_PHRASES:
            log.log_info(f"Skipping Video with id {vid.video_id} because max allowed clickbait phrases in transcript {MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_PHRASES} is exeeded with {pre_validation_result.transcript_clickbait_patterns}")
            return True
        if pre_validation_result.title_emoji_count > MAX_ALLOWED_TITLE_EMOJIS:
            log.log_info(f"Skipping Video with id {vid.video_id} because max allowed emojis in title amoung {MAX_ALLOWED_TITLE_EMOJIS} are exeeded with {pre_validation_result.title_emoji_count} using these emojis: {pre_validation_result.title_emoji_list}")
            return True
        return False

    def validate_metadata(self, vid: Video) -> MetadataValidationResult:
        """
        Method to run the metadata validation that should output raw json, manages the execution of that with retries
        """
        for i in range(3):
            try:
                response: str = self.metadata_validator.validate_metadata(prompt=)
                return self.metadata_validator.validate_ai_response(ai_response=response)
            except EmptyAIResponseError as e:
                log.log_warning(f"The AI response is empty: {str(e)}")
                log.log_info(f"Starting attempt {i+1} of 3")
            except InvalidAIResponseFormatError as e:
                log.log_warning(f"The AI did output invalid JSON: {str(e)}")
                log.log_info(f"Starting attempt {i+1} of 3")


    def validate_video(self, vid: Video, transcript: str) -> ValidationResult:
        # pre-validate
        pre_vali: PreValidationResult = self.pre_validate(vid=vid, raw_transcript=transcript)
        if self.get_pre_validate_hard_stop(pre_validation_result=pre_vali, vid=vid):
            log.log_info(f"The video with id {vid.video_id} contains signs for exessive clickbait, skipping")

if __name__ == "__main__":
    vv = VideoValidator()
    vid = Video(title="Ii😀iIi😀ii😀iiii", url="lasjdlas", author="lsjaflöjd", published="aaioueopr", video_id="sadkasdjfl")
    transcript = "trust me trust me trust me trust me trust me trust me trust me trust me trust me trust me trust me urgent"
    res = vv.pre_validate(vid=vid, raw_transcript=transcript)
    pprint(asdict(res))
    print(vv.get_pre_validate_hard_stop(res, vid))
