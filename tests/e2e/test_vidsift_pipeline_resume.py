from pathlib import Path

import pytest

from tests.fakes.fake_pipeline import (FailingSummarizer,
                                       FailingTranscriptService,
                                       FakeDataCollector, FakeDownloader,
                                       FakeSummarizer, FakeTranscriptService,
                                       FakeValidator, FakeVideoFilter)
from vidsift.config.loader import load_config
from vidsift.config.models import AppConfig
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.ingestion.errors import VideoDataCollectionError
from vidsift.models.video import Video
from vidsift.models.video_record import (VideoProcessingRecord,
                                         VideoProcessingStatus)
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
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
    return load_config(Path(f"{Path(__file__).parent.parent}/fakes/fake_config.toml"))

@pytest.fixture()
def data_collector(fake_config: AppConfig):
    return FakeDataCollector(
        channel_id_list=[
            "UC9x0AN7BWHpCDHSm9NiJFJQ",
            "UC9x0AN7BWHpCDHSm9NiJFJQ"
        ],
        config=fake_config,
        videos=[]
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

def test_resume_validating_videos(
    vid: Video,
    data_collector: FakeDataCollector,
    downloader: FakeDownloader,
    video_validator: FakeValidator,
    video_db: VideoProcessingRepository,
    summarizer: FakeSummarizer,
    default_orchestrator: VidsiftOrchestrator
):
    video_db.open()
    video_db.create(vid=vid)
    video_db.set_status(
        video_id=vid.video_id,
        status=VideoProcessingStatus.VALIDATING
    )
    assert video_db.exists(vid.video_id)

    default_orchestrator.video_data_collector = data_collector

    default_orchestrator.run()

    assert video_validator.validate_calls == 1
    assert downloader.download_calls == 1
    assert summarizer.summarize_calls == 0

    video_db.open()
    assert video_db.get(video_id=vid.video_id).status == VideoProcessingStatus.DONE


def test_resume_downloading_videos(
    vid: Video,
    data_collector: FakeDataCollector,
    downloader: FakeDownloader,
    video_db: VideoProcessingRepository,
    default_orchestrator: VidsiftOrchestrator,
):
    video_db.open()

    video_db.create(vid)
    video_db.set_status(
        video_id=vid.video_id,
        status=VideoProcessingStatus.DOWNLOADING,
    )

    default_orchestrator.video_data_collector = data_collector

    default_orchestrator.run()

    assert downloader.download_calls == 1

    video_db.open()
    assert video_db.get(video_id=vid.video_id).status == VideoProcessingStatus.DONE


def test_resume_summarizing_videos(
    vid: Video,
    data_collector: FakeDataCollector,
    transcript_service: FakeTranscriptService,
    summarizer: FakeSummarizer,
    video_db: VideoProcessingRepository,
    default_orchestrator: VidsiftOrchestrator,
):
    video_db.open()

    video_db.create(vid)
    video_db.set_status(
        video_id=vid.video_id,
        status=VideoProcessingStatus.SUMMARIZING,
    )

    default_orchestrator.video_data_collector = data_collector

    default_orchestrator.run()

    assert transcript_service.transcript_calls == 1
    assert summarizer.summarize_calls == 1

    video_db.open()
    assert video_db.get(video_id=vid.video_id).status == VideoProcessingStatus.DONE
