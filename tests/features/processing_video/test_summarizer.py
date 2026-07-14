from pathlib import Path

import pytest

from tests.fakes.fake_pipeline import (FailingSummarizer,
                                       FailingTranscriptService,
                                       FakeChunkSummarizer, FakeDataCollector,
                                       FakeDownloader, FakeFinalSummarizer,
                                       FakeSummarizer, FakeTranscriptService,
                                       FakeValidator, FakeVideoFilter)
from vidsift.config.loader import load_config
from vidsift.config.models import AppConfig
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.models.video import Video
from vidsift.models.video_record import (VideoProcessingRecord,
                                         VideoProcessingStatus)
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.services.summarization_service import SummarizationService
from vidsift.services.video_data_collection_service import VideoDataCollection
from vidsift.shared.video_discovery_source import DiscoverySource


@pytest.fixture()
def video_validator():
    return FakeValidator(decision="downloaded")

@pytest.fixture()
def transcript_service():
    return FakeTranscriptService()

@pytest.fixture()
def failing_transcript_service():
    return FailingTranscriptService()

@pytest.fixture()
def downloader():
    return FakeDownloader()

@pytest.fixture()
def summarizer():
    return FakeSummarizer()

@pytest.fixture()
def vid():
    return Video("sometitle", "someurl", "someauthor", "UCjjjjjjjjjjjjjjjjjjjjjj", "somepubdate", "uuuuuuuuuuu")

@pytest.fixture()
def fake_config():
    return load_config(Path(f"{Path(__file__).parent.parent.parent}/fakes/fake_config.toml"))

@pytest.fixture()
def data_collector(fake_config: AppConfig):
    return FakeDataCollector(
        channel_id_list=[
            "UC9x0AN7BWHpCDHSm9NiJFJQ",
            "UC9x0AN7BWHpCDHSm9NiJFJQ"
        ],
        config=fake_config
    )

@pytest.fixture()
def video_db(tmp_path, fake_config):
    return VideoProcessingRepository(db_path=tmp_path / "test.db", config=fake_config)

@pytest.fixture()
def video_filter(fake_config):
    return FakeVideoFilter(fake_config)

@pytest.fixture()
def default_orchestrator(fake_config, video_validator, transcript_service, summarizer, downloader, video_filter, video_db):
    return VidsiftOrchestrator(
        config=fake_config,
        video_validator=video_validator,
        transcript_service=transcript_service,
        summarizer=summarizer,
        downloader=downloader,
        video_db=video_db,
        video_filter=video_filter,
        should_sleep=False
    )


def test_no_important_info_summary(
    fake_config: AppConfig,
    vid: Video,
    failing_transcript_service: FailingTranscriptService,
    downloader: FakeDownloader,
    video_validator: FakeValidator,
    video_db: VideoProcessingRepository,
    video_filter: FakeVideoFilter,
    monkeypatch
):
    """
    Tests if each chunk does not contain important information,
    if then the final summarizer does not run cause there is no important information
    """
    summarizer = SummarizationService(config=fake_config)
    summarizer.chunk_summarizer = FakeChunkSummarizer()
    # if it fails, it does not use real ai
    summarizer.final_summarizer = FakeFinalSummarizer()
    summarizer.summarize(
        raw_transcript="raw_transcript",
        vid=vid
    )
    summarizer.final_summarizer.summarize_calls == 0

