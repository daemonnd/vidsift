
from pathlib import Path

from vidsift.config.models import AppConfig
from vidsift.features.summary.chunk_summarizer import ChunkSummaryManager
from vidsift.features.summary.errors import SummaryError
from vidsift.features.summary.final_summarizer import FinalSummarizer
from vidsift.features.validation.errors import EmptyTranscriptError
from vidsift.models.video import Video
from vidsift.shared.AI.errors import AIError
from vidsift.shared.text_normalizer import TextNormalizer


class SummarizationService:
    def __init__(self, config: AppConfig) -> None:
        self.config: AppConfig = config
        self.chunk_summarizer: ChunkSummaryManager = ChunkSummaryManager(config=self.config)
        self.final_summarizer: FinalSummarizer = FinalSummarizer(ai_model=self.config.ai.summary_model)
        self.text_normalizer: TextNormalizer = TextNormalizer()

    def summarize_all_chunks(self, transcript: str) -> list[str]:
        try:
            return self.chunk_summarizer.summarize_all_chunks(transcript=transcript)
        except EmptyTranscriptError as e:
            raise SummaryError(f"An Error occured while summarizing chunks of the transcript: {e}") from e
        # a SummaryError can propagate, cause if will be caught later, in the vidsift pipeline


    def store_summary(self, summary: str, vid: Video) -> None:
        try:
            Path(self.config.summarization.output_dir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise SummaryError(f"OSError: Failed to create directory at {self.config.summarization.output_dir}: {str(e)}") from e
        else:
            dest_file = Path(f"{self.config.summarization.output_dir}/{vid.title}.md")
            try:
                dest_file.touch()
            except FileExistsError as e:
                raise SummaryError(f"FileExistsError: Failed to store the summary at {dest_file}")
            with open(str(dest_file), "w") as f:
                f.write(summary)



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

    def summarize(self, raw_transcript: str, vid: Video) -> str:
        """
        Method to summarize the whole transcript. 
        It calls summarize, store_summaries and summarize_overall and returns the final result
        Raises:
        SummaryError if something went wrong
        Returns: 
        Final String of the AI summary
        """
        transcript: str = self.text_normalizer.normalize(raw_transcript)
        summaries: list[str] = self.summarize_all_chunks(transcript=transcript)
        final_summary: str = self.summarize_overall(summaries=summaries)
        self.store_summary(
            summary=final_summary,
            vid=vid
        )
        return final_summary

if __name__ == "__main__":
    summarization_service = SummarizationService(ai_model="qwen3.5:9b")
    with open("/home/user/projects/python/vidsift/test_data/test_transcript2.txt", "r") as f:
        transcript = f.read()
    summary = summarization_service.summarize(raw_transcript=transcript)
    print("RESULT:")
    print(summary)
