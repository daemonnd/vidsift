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
from vidsift.models.ai_json_requirements import (AIJSONBaseRequirements,
                                                 AIJSONRuntimeRequirements)
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.validation.pre_validation_result import PreValidationResult
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.json_output_manager import AIJsonOutputManager
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
        ai_manager: AIJsonOutputManager = AIJsonOutputManager(
            requirements=AIJSONBaseRequirements(
                system_prompt_filename="metadata_validation.md",
                retry_system_filename="metadata_retry.md",
                output_format_instance=MetadataValidationResult
                )
        )
        try:
            return ai_manager.run_ai_pipeline(
                AIJSONRuntimeRequirements(
                    ai_model="qwen3.5:9b",
                    first_attempt_pattern="$CUSTOM_CHANNEL_INSTRUCTIONS",
                    first_attempt_replacement=config_parser.get_custom_instructions(vid.author),
                    first_attempt_append=f"title: {vid.title}\nauthor: {vid.author}\nurl: {vid.url}\nvideo ID: {vid.video_id}",
                )
            )
        except AIError as e:
            log.log_error(f"AIError during metadata validation: {str(e)}")


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
    print(vv.validate_metadata(vid=vid))
