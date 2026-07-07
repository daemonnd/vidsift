import logging

from vidsift.config.models import AppConfig
from vidsift.features.summary.errors import SummaryError
from vidsift.models.ai_models import AIRequest
from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.executor import AIExecutor
from vidsift.shared.AI.prompt_manager import PromptManager
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.one_retry import retry_once
from vidsift.shared.text_normalizer import TextNormalizer
from vidsift.shared.transcript_chunk_generator import TranscriptChunkGenerator

logger = logging.getLogger(__name__)


class ChunkSummaryManager:
    def __init__(self, config: AppConfig):
        self.config: AppConfig = config
        self.prompt_manager: PromptManager = PromptManager(system_prompt_file_name="chunk_summary.md", config=self.config)
        self.ai_executor: AIExecutor = AIExecutor(config=self.config.ai)
        self.ai_model: str = config.ai.summary_model
        self.transcript_chunk_generator: TranscriptChunkGenerator = TranscriptChunkGenerator(char_chunk_size=self.config.summarization.char_chunk_size)
        self.text_normalizer: TextNormalizer = TextNormalizer()

    @retry_once
    def summarize_chunk(self, chunk: str) -> str:
        """
        Method to run AI against one chunk to get the short bullets summary
        Raises: 
        AIError if the AI usage fails
        Returns: 
        - str of the summary
        """
        try:
            logger.debug(
                "Chunk summarization started.",
                extra={
                    "event": LogEvent.CHUNK_SUMMARIZATION_STARTED,
                    "model": self.ai_model,
                    "chunk_length": len(chunk),
                },
            )

            ai_request: AIRequest = AIRequest(
                prompt=self.prompt_manager.generate_prompt(
                        append=chunk,
                    ),
                model=self.config.ai.summary_model,
                max_tokens=150,
                context_length=self.config.ai.summary_model_context_length,
                thinking=self.config.ai.chunk_summary_think
            )
            summary = str(self.ai_executor.generate(request=ai_request).content)

            normalized_summary = self.text_normalizer.normalize(summary)


        except AIError as e:
            logger.exception(
                "Chunk summarization failed.",
                extra={
                    "event": LogEvent.CHUNK_SUMMARIZATION_FAILED,
                    "model": self.ai_model,
                    "chunk_length": len(chunk),
                },
                exc_info=True,
            )
            raise SummaryError(f"An error occurred during chunk summarization: {e}") from e

        else:
            logger.info(
                "Chunk summarization completed.",
                extra={
                    "event": LogEvent.CHUNK_SUMMARIZATION_COMPLETED,
                    "model": self.ai_model,
                    "chunk_length": len(chunk),
                    "summary_length": len(normalized_summary),
                },
            )

            return normalized_summary

    def summarize_all_chunks(self, transcript: str, video_id: str) -> list[str]:
        """
        Method to summarize all the chunks.
        Raises:
        - SummaryError if a SummaryError occured while summarizing one chunk
        - EmptyTranscriptError if the transcript cannot be chunked because it is empty
        """
        transcript_chunks = self.transcript_chunk_generator.build_chunks(
            self.transcript_chunk_generator.split_into_sentences(transcript=transcript))

        logger.info(
            "Transcript chunk summarization started.",
            extra={
                "event": LogEvent.TRANSCRIPT_SUMMARIZATION_STARTED,
            },
        )

        summaries: list[str] = []
        summary: str = ""
        total_chunks: int = 0

        for chunk, chunk_index in transcript_chunks:
            total_chunks += 1
            logger.debug(
                f"Processing  chunk {chunk_index+1}...",
                extra={
                    "event": LogEvent.CHUNK_SUMMARIZATION_STARTED,
                    "video_id": video_id,
                    "chunk_index": chunk_index,
                    "chunk_length": len(chunk),
                },
            )

            try:
                summary = self.summarize_chunk(chunk)

            except SummaryError as e:
                logger.warning(
                    f"Failed to summarize transcript chunk, some important information in the final summary may be missing: {str(e)}",
                    extra={
                        "event": LogEvent.CHUNK_SUMMARIZATION_FAILED,
                        "video_id": video_id,
                        "chunk_index": chunk_index,
                        "chunk_length": len(chunk),
                    },
                    exc_info=True,
                )
                continue

            if summary.strip() == "NO_IMPORTANT_INFORMATION":
                logger.debug(
                    "Chunk contained no important information.",
                    extra={
                        "event": LogEvent.CHUNK_SUMMARIZATION_COMPLETED,
                        "video_id": video_id,
                        "chunk_index": chunk_index,
                        "chunk_length": len(chunk),
                        "contains_important_information": False,
                    },
                )
                continue

            summaries.append(summary)

        logger.debug(
            "Transcript chunk summarization completed.",
            extra={
                "event": LogEvent.TRANSCRIPT_SUMMARIZATION_COMPLETED,
                "video_id": video_id,
                "total_chunks": total_chunks,
                "successful_summaries": len(summaries),
            },
        )

        return summaries
