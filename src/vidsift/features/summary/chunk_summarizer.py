from vidsift.config.parser import AI_MODEL, SUMMARIZATION_CHAR_CHUNK_SIZE
from vidsift.features.summary.errors import SummaryError
from vidsift.shared.AI.errors import AIError
from vidsift.shared.AI.run_model import AIUsageManager
from vidsift.shared.errorprotocol import logger
from vidsift.shared.one_retry import retry_once
from vidsift.shared.text_normalizer import TextNormalizer
from vidsift.shared.transcript_chunk_generator import TranscriptChunkGenerator

log: logger = logger()


class ChunkSummaryManager:
    def __init__(self, ai_model: str = AI_MODEL):
        self.chunk_summary_ai: AIUsageManager = AIUsageManager(system_prompt_file_name="chunk_summary.md")
        self.ai_model: str = ai_model
        self.transcript_chunk_generator: TranscriptChunkGenerator = TranscriptChunkGenerator(char_chunk_size=SUMMARIZATION_CHAR_CHUNK_SIZE)
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
            summary: str = self.chunk_summary_ai.run_ai(
                prompt=self.chunk_summary_ai.generate_prompt(
                    append=chunk,
                    )
                , model=self.ai_model
            )
            return self.text_normalizer.normalize(summary)
        except AIError as e:
            raise SummaryError(f"An error occurred during chunk summarization: {e}") from e

    def summarize_all_chunks(self, transcript: str) -> list[str]:
        """
        Method to summarize all the chunks.
        Raises:
        - SummaryError if a SummaryError occured while summarizing one chunk
        - EmptyTranscriptError if the transcript cannot be chunked because it is empty
        """
        self.transcript_chunks = self.transcript_chunk_generator.build_chunks(
            self.transcript_chunk_generator.split_into_sentences(transcript=transcript))
        summaries: list[str] = []
        summary: str = ""
        for chunk, chunk_index in self.transcript_chunks:
            log.log_debug(f"Summarizing chunk {chunk_index + 1} with length {len(chunk)} characters...")
            try:
                summary = self.summarize_chunk(chunk)
            except SummaryError as e:
                log.log_warning(f"SummaryError: Failed to summarized one transcript chunk, some important information in the final summary may be missing: {str(e)}")
                continue
            if summary.strip() == "NO_IMPORTANT_INFORMATION":
                continue
            summaries.append(summary)

        return summaries
