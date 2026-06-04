"""
File for managing the validation process and returning the score of the video
"""
from dataclasses import asdict
from typing import Literal

from vidsift.config.parser import ConfigParser
from vidsift.features.validation.decision_engine import DecisionEngine
from vidsift.features.validation.errors import VideoValidationError
from vidsift.features.validation.metadata_validator import MetadataValidator
from vidsift.features.validation.pre_validation.metrics_counter import \
    PreValidator
from vidsift.features.validation.pre_validation.score_calculator import \
    PreValidationScoreCalculator
from vidsift.features.validation.transcript_validator.transcript_chunk_provider import \
    TranscriptChunkProvider
from vidsift.models.ai_json_requirements import (AIJSONBaseRequirements,
                                                 AIJSONRuntimeRequirements)
from vidsift.models.validation.metadata_validation_result import \
    MetadataValidationResult
from vidsift.models.validation.pre_validation_result import PreValidationResult
from vidsift.models.validation.transcript_validation_result import \
    TranscriptValidationResult
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
        self.transcript_chunk_provider: TranscriptChunkProvider = TranscriptChunkProvider()

    @log.log
    def pre_validate(self, vid: Video, transcript: str) -> bool:
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
        Raises:
        VideoValidationError: If the AI fails to validate the metadata after the maximum number of retries, or if any unexpected error occurs during the validation process.
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
            raise VideoValidationError(f"Metadata validation failed for video with id {vid.video_id} due to AI error: {str(e)}") from e


    def validate_transcript(self, vid: Video, transcript: str) -> TranscriptValidationResult:
        """
        Method to run the transcript validation that should output raw json, manages the execution of that with retries
        Raises:
        VideoValidationError: If the AI fails to validate the transcript after the maximum number of retries, or if any unexpected error occurs during the validation process.
        """

        chunks: str = self.transcript_chunk_provider.get_necessary_chunks(transcript=transcript)

        ai_manager: AIJsonOutputManager = AIJsonOutputManager(
            requirements=AIJSONBaseRequirements(
                system_prompt_filename="transcript_validation.md",
                retry_system_filename="transcript_retry.md",
                output_format_instance=TranscriptValidationResult
            )
        )
        try:
            return ai_manager.run_ai_pipeline(
                AIJSONRuntimeRequirements(
                    ai_model="qwen3.5:9b",
                    first_attempt_pattern="$CUSTOM_CHANNEL_INSTRUCTIONS",
                    first_attempt_replacement=config_parser.get_custom_instructions(vid.author),
                    first_attempt_append=f"\n{chunks}",
                )
            )
        except AIError as e:
            log.log_error(f"AIError during transcript validation: {str(e)}")
            raise VideoValidationError(f"Transcript validation failed for video with id {vid.video_id} due to AI error: {str(e)}")



    @log.log
    def validate_video(self, vid: Video, raw_transcript: str) -> Literal["download", "summarize", "discard"]:
        # normalize the transcript
        transcript: str = self.text_normalizer.normalize(raw_transcript)

        # pre-validate
        if not self.pre_validate(vid=vid, transcript=transcript):
            log.log_info(f"The video with id {vid.video_id} contains signs for exessive clickbait, skipping")
            return "discard"
        else:
            log.log_info(f"The video with id {vid.video_id} does not contain strong signs of clickbait, moving to metadata validation")

        # metadata validation
        log.log_info(f"Starting metadata validation for video with id {vid.video_id}")
        metadata_validation_result: MetadataValidationResult = self.validate_metadata(vid=vid)
        if metadata_validation_result.flags:
            log.log_info(f"Metadata validation result for video with id {vid.video_id} revealed the following flags: {metadata_validation_result.flags}.")
        log.log_debug(f"Metadata validation for video with id {vid.video_id} metadata_score: {metadata_validation_result.metadata_score}")
        log.log_debug(f"Metadata validation for video with id {vid.video_id} topic_match_score: {metadata_validation_result.topic_match_score}")
        log.log_debug(f"Metadata validation for video with id {vid.video_id} confidence: {metadata_validation_result.confidence}")
        log.log_debug(f"Metadata validation for video with id {vid.video_id} summary_reason: {metadata_validation_result.summary_reason}")
        log.log_debug(f"Metadata validation for video with id {vid.video_id} flags: {metadata_validation_result.flags}")


        # transcript validation
        log.log_info(f"Starting transcript validation for video with id {vid.video_id}")
        transcript_validation_result: TranscriptValidationResult = self.validate_transcript(vid=vid, transcript=transcript)
        if transcript_validation_result.flags:
            log.log_info(f"Transcript validation result for video with id {vid.video_id} revealed the following flags: {transcript_validation_result.flags}.")
        log.log_debug(f"Transcript validation for video with id {vid.video_id} content_quality_score: {transcript_validation_result.content_quality_score}")
        log.log_debug(f"Transcript validation for video with id {vid.video_id} topic_match_score: {transcript_validation_result.topic_match_score}")
        log.log_debug(f"Transcript validation for video with id {vid.video_id} confidence: {transcript_validation_result.confidence}")
        log.log_debug(f"Transcript validation for video with id {vid.video_id} summary_reason: {transcript_validation_result.summary_reason}")
        log.log_debug(f"Transcript validation for video with id {vid.video_id} flags: {transcript_validation_result.flags}")

        # decision engine
        decision_engine: DecisionEngine = DecisionEngine(metadata_result=metadata_validation_result, transcript_result=transcript_validation_result)
        return decision_engine.make_decision(decision_engine.calculate_decision_scores())



if __name__ == "__main__":
    vv = VideoValidator()
    vid = Video(title="i didn't want to like this", url="https://www.youtube.com/watch?v=G3jvn7n-68Y", author="NetworkChuck", published="32497954", video_id="G3jvn7n-68Y")
    with open("/home/user/projects/python/vidsift/fake-transcript.txt", "r") as f:
        transcript = f.read()
    with open("/home/user/projects/python/vidsift/test_data/test_transcript2.txt", "r") as f:
        transcript2 = f.read()
    result = vv.validate_video(vid=vid, raw_transcript=transcript)
    print("RESULT:")
    print(result)
    vid = Video(title="i didn't want to like this", url="https://www.youtube.com/watch?v=G3jvn7n-68Y", author="NetworkChuck", published="32497954", video_id="G3jvn7n-68Y")
    result2 = vv.validate_video(vid=vid, raw_transcript=transcript2)
    print("RESULT2:")
    print(result2)

