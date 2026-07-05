
import logging
from pathlib import Path

from pathvalidate import sanitize_filename

from vidsift.config.models import AppConfig
from vidsift.features.summary.chunk_summarizer import ChunkSummaryManager
from vidsift.features.summary.errors import SummaryError
from vidsift.features.summary.final_summarizer import FinalSummarizer
from vidsift.features.validation.errors import EmptyTranscriptError
from vidsift.models.video import Video
from vidsift.shared.AI.errors import AIError
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.one_retry import retry_once
from vidsift.shared.text_normalizer import TextNormalizer

logger = logging.getLogger(__name__)


class SummarizationService:
    def __init__(self, config: AppConfig) -> None:
        self.config: AppConfig = config
        self.chunk_summarizer: ChunkSummaryManager = ChunkSummaryManager(config=self.config)
        self.final_summarizer: FinalSummarizer = FinalSummarizer(ai_model=self.config.ai.summary_model, config=self.config)
        self.text_normalizer: TextNormalizer = TextNormalizer()

    def summarize_all_chunks(self, transcript: str, video_id: str) -> list[str]:
        try:
            return self.chunk_summarizer.summarize_all_chunks(transcript=transcript, video_id=video_id)
        except EmptyTranscriptError as e:
            raise SummaryError(f"An Error occured while summarizing chunks of the transcript: {e}") from e
        # a SummaryError can propagate, cause if will be caught later, in the vidsift pipeline


    def store_summary(self, summary: str, vid: Video) -> Path:
        try:
            Path(self.config.summarization.output_dir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise SummaryError(f"OSError: Failed to create directory at {self.config.summarization.output_dir}: {str(e)}") from e
        else:
            dest_file_name = f"{vid.title}_{vid.video_id}.md"
            dest_file = Path(f"{self.config.summarization.output_dir}/{sanitize_filename(dest_file_name)}")
            try:
                dest_file.touch()
            except FileExistsError as e:
                raise SummaryError(f"FileExistsError: Failed to store the summary at {dest_file}: {str(e)}")
            else:
                with open(str(dest_file), "w") as f:
                    f.write(summary)
                return dest_file



    @retry_once
    def summarize_overall(self, summaries: list[str]) -> str:
        """
        Method to summarize all the short, bulleted summaries
        Raises: 
        AIError if the summarizer fails
        Returns:
        str of the final summary
        """
        try:
            return self.final_summarizer.summarize(summaries)
        except AIError as e:
            raise SummaryError(f"An error occured while summarizing the short summaries of the chunks: {e}") from e

    def summarize(self, raw_transcript: str, vid: Video) -> None:
        """
        Method to summarize the whole transcript.
        It calls summarize, store_summaries and summarize_overall and returns the final result
        Raises:
        SummaryError if something went wrong
        Returns: 
        Final String of the AI summary
        """
        transcript: str = self.text_normalizer.normalize(raw_transcript)
        summaries: list[str] = self.summarize_all_chunks(transcript=transcript, video_id=vid.video_id)
        final_summary: str = self.summarize_overall(summaries=summaries)
        dest_path: Path = self.store_summary(
            summary=final_summary,
            vid=vid
        )
        logger.info(
            f"Finished summarizing video with video id '{vid.video_id}', the summary got saved to '{dest_path}'",
            extra={
                "event": LogEvent.VIDEO_SUMMARIZATION_COMPLETED,
                "video_id": vid.video_id,
                "output_file": str(dest_path)
            }
        )

if __name__ == "__main__":
    summarization_service = SummarizationService(ai_model="qwen3.5:9b")
    with open("/home/user/projects/python/vidsift/test_data/test_transcript2.txt", "r") as f:
        transcript = f.read()
    summary = summarization_service.summarize(raw_transcript=transcript)
    print("RESULT:")
    print(summary)
