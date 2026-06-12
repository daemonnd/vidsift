import logging

from vidsift.config import CONFIG
from vidsift.features.summary.errors import SummaryError
from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.run_model import AIUsageManager
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.one_retry import retry_once
from vidsift.shared.text_normalizer import TextNormalizer
from vidsift.shared.transcript_chunk_generator import TranscriptChunkGenerator

logger = logging.getLogger(__name__)


class ChunkSummaryManager:
    def __init__(self, ai_model: str = CONFIG.ai.summary_model):
        self.chunk_summary_ai: AIUsageManager = AIUsageManager(system_prompt_file_name="chunk_summary.md")
        self.ai_model: str = ai_model
        self.transcript_chunk_generator: TranscriptChunkGenerator = TranscriptChunkGenerator(char_chunk_size=CONFIG.summarization.char_chunk_size)
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

            summary: str = self.chunk_summary_ai.run_ai(
                prompt=self.chunk_summary_ai.generate_prompt(
                    append=chunk,
                    )
                , model=self.ai_model
            )

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

    def summarize_all_chunks(self, transcript: str) -> list[str]:
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

        for chunk, chunk_index in transcript_chunks:
            logger.debug(
                "Chunk summarization processing.",
                extra={
                    "event": LogEvent.CHUNK_SUMMARIZATION_STARTED,
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
                        "chunk_index": chunk_index,
                        "chunk_length": len(chunk),
                        "contains_important_information": False,
                    },
                )
                continue

            summaries.append(summary)

        logger.info(
            "Transcript chunk summarization completed.",
            extra={
                "event": LogEvent.TRANSCRIPT_SUMMARIZATION_COMPLETED,
                "successful_summaries": len(summaries),
            },
        )

        return summaries
