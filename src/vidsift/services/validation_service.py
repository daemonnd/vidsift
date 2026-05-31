"""
File for managing the validation process and returning the score of the video
"""
from dataclasses import asdict

from vidsift.config.parser import ConfigParser
from vidsift.features.validation.errors import VideoValidationError
from vidsift.features.validation.metadata_validator import MetadataValidator
from vidsift.features.validation.pre_validation.metrics_counter import \
    PreValidator
from vidsift.features.validation.pre_validation.score_calculator import \
    PreValidationScoreCalculator
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.validation.pre_validation_result import PreValidationResult
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.shared.AI.run_model import AIUsageManager
from vidsift.shared.errorprotocol import logger
from vidsift.shared.text_normalizer import TextNormalizer

log: logger = logger()
config_parser: ConfigParser = ConfigParser()


class VideoValidator:
    def __init__(self) -> None:
        self.pre_validator: PreValidator = PreValidator()
        self.text_normalizer: TextNormalizer = TextNormalizer()
        self.metadata_validator: MetadataValidator = MetadataValidator()
        self.pre_validation_score_calculator: PreValidationScoreCalculator = PreValidationScoreCalculator()

    @log.log
    def pre_validate(self, vid: Video, raw_transcript: str) -> bool:
        """
        Method to run the pre validator, without using AI
        returns True if the video does not seem to be clickbait, False if it is
        """
        title: str = self.text_normalizer.normalize(vid.title)
        new_vid: Video = Video(
                title=title,
                url=vid.url,
                author=vid.author,
                published=vid.published,
                video_id=vid.video_id,
        )
        transcript: str = self.text_normalizer.normalize(raw_transcript)

        pre_vali_result: PreValidationResult =  self.pre_validator.build_pre_validation_features(vid=new_vid, transcript=transcript)
        log.log_debug(f"Pre-validation result: {asdict(pre_vali_result)}")

        pre_vali_calc_result, reason = self.pre_validation_score_calculator.calculate_score(result=pre_vali_result)
        if pre_vali_calc_result > 0.5:
            log.log_info(f"Video with id {vid.video_id} is likely to be clickbait with a score of {pre_vali_calc_result:.2f}. Reason: {reason}")
            return False
        else:
            log.log_info(f"Video with id {vid.video_id} is unlikely to be clickbait with a score of {pre_vali_calc_result:.2f}. Reason: {reason}")
            return True



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
        if not self.pre_validate(vid=vid, raw_transcript=transcript):
            log.log_info(f"The video with id {vid.video_id} contains signs for exessive clickbait, skipping")
            return ValidationResult(metadata_score=-1, total_transcript_score=-1, flags= ["excessive_clickbait_signs"])
        else:
            log.log_info(f"The video with id {vid.video_id} does not contain strong signs of clickbait, moving to metadata validation")

        metadata_validation_result: MetadataValidationResult = self.validate_metadata(vid=vid)

if __name__ == "__main__":
    vv = VideoValidator()
    vid = Video(title="Iiiiiii😀iiii", url="lasjdlas", author="NetworkChuck", published="aaioueopr", video_id="sadkasdjfl")
    transcript = ". or no python. Python is a programming language. it is really popular. me "
    print(vv.pre_validate(vid=vid, raw_transcript=transcript))
