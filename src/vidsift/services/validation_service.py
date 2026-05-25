"""
File for managing the validation process and returning the score of the video
"""
from dataclasses import asdict
from pprint import pprint

from vidsift.config.parser import (MAX_ALLOWED_TITLE_CAPITAL_RATIO,
                                   MAX_ALLOWED_TITLE_CLICKBAIT_PHRASES,
                                   MAX_ALLOWED_TITLE_EMOJIS,
                                   MAX_ALLOWED_TRANSCRIPT_CLICKBAIT_PHRASES,
                                   ConfigParser)
from vidsift.features.validation.errors import (EmptyAIResponseError,
                                                InvalidAIResponseFormatError,
                                                VideoValidationError)
from vidsift.features.validation.metadata_validator import MetadataValidator
from vidsift.features.validation.pre_validation import PreValidator
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.validation.pre_validation_result import PreValidationResult
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.shared.ai_runner import AIUsageManager
from vidsift.shared.errorprotocol import logger
from vidsift.shared.text_normalizer import TextNormalizer

log: logger = logger()
config_parser: ConfigParser = ConfigParser()


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
        title_uppercase_ratio: float = (max(title_uppercase_chars, 1) / max(title_char_length, 1) * 100) # to get the result in percent

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
            log.log_info(f"Skipping Video with id {vid.video_id} because max allowed emojis in title amount {MAX_ALLOWED_TITLE_EMOJIS} are exeeded with {pre_validation_result.title_emoji_count} using these emojis: {pre_validation_result.title_emoji_list}")
            return True
        return False

    def validate_metadata(self, vid: Video) -> MetadataValidationResult:
        """
        Method to run the metadata validation that should output raw json, manages the execution of that with retries
        """
        validation_ai: AIUsageManager = AIUsageManager("metadata_validation.md")
        retry_system_ai: AIUsageManager = AIUsageManager("metadata_retry.md")
        ai_executor: AIUsageManager = AIUsageManager("")
        for i in range(3):
            log.log_info(f"Starting attempt {i+1} of 3")

            # on the first attempt
            if i == 0:
                # get the prompt
                prompt: str = validation_ai.generate_prompt(
                    pattern="$CUSTOM_CHANNEL_INSTRUCTIONS", 
                    replacement=config_parser.get_custom_instructions(creator=vid.author),
                    append=f"title: {vid.title}\nauthor: {vid.author}\nurl: {vid.url}\nvideo ID: {vid.video_id}"
                )
                print(f"prompt: {prompt}")

            # for the attempts that come after, when response and error message exist
            else:
                # get the prompt
                prompt: str = retry_system_ai.generate_prompt(
                            system_prompt=retry_system_ai.generate_prompt(
                            pattern="$ERROR_MESSAGE",
                            replacement=error_msg,
                        ),
                        pattern="$PREVIOUS_AI_OUTPUT",
                        replacement=response,
                    )
                print(f"prompt: {prompt}")
            try:
                response: str = ai_executor.run_ai(prompt=prompt, model="qwen3.5:9b")
                print(f"response: {response}")
                return self.metadata_validator.validate_ai_response(ai_response=response)
            except EmptyAIResponseError as e:
                error_msg: str = str(e)
                response: str = ""
                log.log_warning(f"EmptyAIResponseError: {str(e)}")
            except InvalidAIResponseFormatError as e:
                error_msg: str = str(e)
                log.log_warning(f"The AI did output invalid JSON: {str(e)}")
        raise VideoValidationError("After 3 attempts, the AI output does not match the required JSON")


    def validate_video(self, vid: Video, transcript: str) -> ValidationResult:
        # pre-validate
        pre_vali: PreValidationResult = self.pre_validate(vid=vid, raw_transcript=transcript)
        if self.get_pre_validate_hard_stop(pre_validation_result=pre_vali, vid=vid):
            log.log_info(f"The video with id {vid.video_id} contains signs for exessive clickbait, skipping")

if __name__ == "__main__":
    vv = VideoValidator()
    vid = Video(title="Ii😀iIi😀ii😀iiii", url="lasjdlas", author="NetworkChuck", published="aaioueopr", video_id="sadkasdjfl")
    transcript = "trust me trust me trust me trust me trust me trust me trust me trust me trust me trust me trust me urgent"
    res = vv.pre_validate(vid=vid, raw_transcript=transcript)
    pprint(asdict(res))
    print(vv.get_pre_validate_hard_stop(res, vid))

    print(vv.validate_metadata(vid=vid))
