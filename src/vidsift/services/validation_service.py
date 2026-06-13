"""
File for managing the validation process and returning the score of the video
"""
import logging
from dataclasses import asdict

from vidsift.config import CONFIG
from vidsift.features.validation.decision_engine import DecisionEngine
from vidsift.features.validation.errors import VideoValidationError
from vidsift.features.validation.instruction_provider import \
    get_custom_instructions
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
from vidsift.models.validation.validation_result import ValidationResult
from vidsift.models.video import Video
from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.json_output_manager import AIJsonOutputManager
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.text_normalizer import TextNormalizer

logger = logging.getLogger(__name__)


class VideoValidator:
    def __init__(self) -> None:
        self.pre_validator: PreValidator = PreValidator()
        self.text_normalizer: TextNormalizer = TextNormalizer()
        self.pre_validation_score_calculator: PreValidationScoreCalculator = PreValidationScoreCalculator()
        self.transcript_chunk_provider: TranscriptChunkProvider = TranscriptChunkProvider()

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
            channel_id=vid.channel_id,
        )

        pre_vali_result: PreValidationResult = self.pre_validator.build_pre_validation_features(
            vid=new_vid, transcript=transcript
        )

        logger.debug(
            "Pre-validation completed.",
            extra={
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
                "pre_validation": asdict(pre_vali_result),
            },
        )

        pre_vali_calc_result, reason = self.pre_validation_score_calculator.calculate_score(result=pre_vali_result)
        if pre_vali_calc_result > 0.5:
            logger.info(
                f"Video {vid.video_id} classified as likely clickbait.",
                extra={
                    "event": LogEvent.VIDEO_VALIDATION_COMPLETED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "decision": "discarded",
                    "pre_validation_score": round(pre_vali_calc_result, 2),
                    "reason": reason,
                },
            )
            return False
        else:
            logger.info(
                f"Video {vid.video_id} passed pre-validation.",
                extra={
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "pre_validation_score": round(pre_vali_calc_result, 2),
                    "reason": reason,
                },
            )
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
                output_format_instance=MetadataValidationResult,
            )
        )
        try:
            return ai_manager.run_ai_pipeline(
                AIJSONRuntimeRequirements(
                    ai_model=CONFIG.ai.validation_model,
                    first_attempt_pattern="$CUSTOM_CHANNEL_INSTRUCTIONS",
                    first_attempt_replacement=get_custom_instructions(vid.author),
                    first_attempt_append=f"title: {vid.title}\nauthor: {vid.author}\nurl: {vid.url}\nvideo ID: {vid.video_id}",
                )
            )
        except AIError:
            logger.exception(
                f"Metadata validation failed for video {vid.video_id}.",
                extra={
                    "event": LogEvent.VIDEO_VALIDATION_FAILED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "validation_stage": "metadata",
                },
            )
            raise VideoValidationError(f"Metadata validation failed for video {vid.video_id} due to AI error")

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
                output_format_instance=TranscriptValidationResult,
            )
        )
        try:
            return ai_manager.run_ai_pipeline(
                AIJSONRuntimeRequirements(
                    ai_model="qwen3.5:9b",
                    first_attempt_pattern="$CUSTOM_CHANNEL_INSTRUCTIONS",
                    first_attempt_replacement=get_custom_instructions(vid.author),
                    first_attempt_append=f"\n{chunks}",
                )
            )
        except AIError as e:
            logger.exception(
                f"Transcript validation failed for video {vid.video_id}.",
                extra={
                    "event": LogEvent.VIDEO_VALIDATION_FAILED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "validation_stage": "transcript",
                },
            )
            raise VideoValidationError(f"Transcript validation failed for video {vid.video_id} due to AI error: {str(e)}")

    def validate_video(self, vid: Video, raw_transcript: str) -> ValidationResult:
        logger.info(
            f"Starting validation for video {vid.video_id}.",
            extra={
                "event": LogEvent.VIDEO_VALIDATION_STARTED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
            },
        )

        transcript: str = self.text_normalizer.normalize(raw_transcript)

        if not self.pre_validate(vid=vid, transcript=transcript):
            logger.info(
                f"Video {vid.video_id} discarded because of excessive clickbait indicators.",
                extra={
                    "event": LogEvent.VIDEO_VALIDATION_COMPLETED,
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "decision": "discarded",
                },
            )
            return ValidationResult(
                content_quality_score=0.1,
                topic_match_score=0.1,
                decision="discarded",
                summary_reason={"reason": "signs of exessive clickbait are present"},
            )
        else:
            logger.info(
                f"Video {vid.video_id} passed pre-validation.",
                extra={
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                },
            )

        logger.info(
            f"Starting metadata validation for video {vid.video_id}.",
            extra={
                "event": LogEvent.VIDEO_VALIDATION_STARTED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
                "validation_stage": "metadata",
            },
        )
        metadata_validation_result: MetadataValidationResult = self.validate_metadata(vid=vid)
        if metadata_validation_result.flags:
            logger.info(
                f"Metadata validation detected flags for video {vid.video_id}.",
                extra={
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "validation_stage": "metadata",
                    "metadata_score": metadata_validation_result.metadata_score,
                    "topic_match_score": metadata_validation_result.topic_match_score,
                    "confidence": metadata_validation_result.confidence,
                    "flags": sorted(metadata_validation_result.flags),
                    "reason": metadata_validation_result.summary_reason
                },
            )
        logger.debug(
            "Metadata validation completed.",
            extra={
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
                "metadata_score": metadata_validation_result.metadata_score,
                "topic_match_score": metadata_validation_result.topic_match_score,
                "confidence": metadata_validation_result.confidence,
                "flags": sorted(metadata_validation_result.flags),
                "reason": metadata_validation_result.summary_reason,
            },
        )

        # transcript validation
        logger.info(
            f"Starting transcript validation for video {vid.video_id}.",
            extra={
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
                "validation_stage": "transcript",
            },
        )
        transcript_validation_result: TranscriptValidationResult = self.validate_transcript(vid=vid, transcript=transcript)
        if transcript_validation_result.flags:
            logger.info(
                f"Transcript validation detected flags for video {vid.video_id}.",
                extra={
                    "video_id": vid.video_id,
                    "channel_id": vid.channel_id,
                    "validation_stage": "transcript",
                    "score": transcript_validation_result.content_quality_score,
                    "topic_match_score": transcript_validation_result.topic_match_score,
                    "confidence": transcript_validation_result.confidence,
                    "flags": sorted(transcript_validation_result.flags),
                    "reason": transcript_validation_result.summary_reason
                },
            )
        logger.debug(
            "Transcript validation completed.",
            extra={
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
                "score": transcript_validation_result.content_quality_score,
                "topic_match_score": transcript_validation_result.topic_match_score,
                "confidence": transcript_validation_result.confidence,
                "reason": transcript_validation_result.summary_reason,
                "flags": sorted(transcript_validation_result.flags),
            },
        )

        decision_engine: DecisionEngine = DecisionEngine(
            metadata_result=metadata_validation_result, transcript_result=transcript_validation_result
        )
        validation_result = decision_engine.make_decision(decision_engine.calculate_decision_scores())

        logger.info(
            f"Validation completed for video {vid.video_id}.",
            extra={
                "event": LogEvent.VIDEO_VALIDATION_COMPLETED,
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
                "decision": validation_result.decision,
                "score": validation_result.content_quality_score,
                "topic_match_score": validation_result.topic_match_score,
                "reason": validation_result.summary_reason,
            },
        )

        return validation_result


if __name__ == "__main__":
    vv = VideoValidator()
    vid = Video(
        title="i didn't want to like this",
        url="https://www.youtube.com/watch?v=G3jvn7n-68Y",
        author="NetworkChuck",
        published="32497954",
        video_id="G3jvn7n-68Y",
        channel_id="alsdjöasdjf",
    )
    with open("/home/user/projects/python/vidsift/fake-transcript.txt", "r") as f:
        transcript = f.read()
    with open("/home/user/projects/python/vidsift/test_data/test_transcript2.txt", "r") as f:
        transcript2 = f.read()
    result = vv.validate_video(vid=vid, raw_transcript=transcript)
    print("RESULT:")
    print(result)
    vid = Video(
        title="i didn't want to like this",
        url="https://www.youtube.com/watch?v=G3jvn7n-68Y",
        author="NetworkChuck",
        published="32497954",
        video_id="G3jvn7n-68Y",
        channel_id="asdojlöasdjlöaslödf",
    )
    result2 = vv.validate_video(vid=vid, raw_transcript=transcript2)
    print("RESULT2:")
    print(result2)
