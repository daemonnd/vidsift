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
def test_validation_downloads_video(
    default_orchestrator: VidsiftOrchestrator,
    fake_config,
    video_validator,
    downloader,
):
    default_orchestrator.video_data_collector = FakeDataCollector(
        channel_id_list=["UCo71RUe6DX4w-Vd47rFLXPg"],
        config=fake_config,
        videos=[
            (Video(
                title="",
                author="",
                channel_id="UCo71RUe6DX4w-Vd47rFLXPg",
                published="",
                video_id="12345678910",
                url=""
            ), DiscoverySource.RSS),
        ],
    )

    default_orchestrator.run()

    assert video_validator.validate_calls == 1
    assert downloader.download_calls == 1


def test_existing_video_is_skipped(
    default_orchestrator: VidsiftOrchestrator,
    fake_config: AppConfig,
    video_db: VideoProcessingRepository,
    vid: Video,
    downloader: FakeDownloader,
    video_validator: FakeValidator,
    transcript_service: FakeTranscriptService,
):
    # Arrange
    video_db.open()
    video_db.create(vid)
    video_db.set_status(
        video_id=vid.video_id,
        status=VideoProcessingStatus.DONE
    )

    default_orchestrator.video_data_collector = FakeDataCollector(
        channel_id_list=[vid.channel_id],
        config=fake_config,
        videos=[
            (vid, DiscoverySource.RSS),
        ],
    )

    # Act
    default_orchestrator.run()

    # Assert
    assert video_validator.validate_calls == 0
    assert transcript_service.transcript_calls == 0
    assert downloader.download_calls == 0

def test_transcript_failure_stops_processing(
    fake_config: AppConfig,
    vid: Video,
    failing_transcript_service: FailingTranscriptService,
    downloader: FakeDownloader,
    video_validator: FakeValidator,
    video_db: VideoProcessingRepository,
    video_filter: FakeVideoFilter,
    summarizer: FakeSummarizer,
):
    orchestrator = VidsiftOrchestrator(
        config=fake_config,
        video_validator=video_validator,
        transcript_service=failing_transcript_service,
        summarizer=summarizer,
        downloader=downloader,
        video_db=video_db,
        video_filter=video_filter,
        should_sleep=False
    )

    orchestrator.transcript_service = failing_transcript_service

    orchestrator.video_data_collector = FakeDataCollector(
        channel_id_list=[vid.channel_id],
        config=fake_config,
        videos=[
            (vid, DiscoverySource.RSS),
        ],
    )

    orchestrator.run()

    assert failing_transcript_service.transcript_calls == 1
    assert video_validator.validate_calls == 0
    assert downloader.download_calls == 0
