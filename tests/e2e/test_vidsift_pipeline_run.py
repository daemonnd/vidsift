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
from vidsift.models.video_record import VideoProcessingStatus
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
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
def download_vid():
    return Video("sometitle", "someurl", "someauthor", "UC9x0AN7BWHpCDHSm9NiJFJQ", "somepubdate", "uuuuuuuuuuu")

@pytest.fixture()
def summarize_vid():
    return Video("sometitle", "someurl", "someauthor", "UC4JX40jDee_tINbkjycV4Sg", "somepubdate", "uuuuuuuuuuu")

@pytest.fixture()
def validate_vid():
    return Video("sometitle", "someurl", "someauthor", "UCo71RUe6DX4w-Vd47rFLXPg", "somepubdate", "uuuuuuuuuuu")

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
        should_sleep=False,
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
    download_vid: Video,
    downloader: FakeDownloader,
    video_validator: FakeValidator,
    transcript_service: FakeTranscriptService,
):
    # Arrange
    video_db.open()
    video_db.create(download_vid)
    video_db.set_status(
        video_id=download_vid.video_id,
        status=VideoProcessingStatus.DONE
    )

    default_orchestrator.video_data_collector = FakeDataCollector(
        channel_id_list=[download_vid.channel_id],
        config=fake_config,
        videos=[
            (download_vid, DiscoverySource.RSS),
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
    validate_vid: Video,
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

    #orchestrator.transcript_service = failing_transcript_service

    orchestrator.video_data_collector = FakeDataCollector(
        channel_id_list=[validate_vid.channel_id],
        config=fake_config,
        videos=[
            (validate_vid, DiscoverySource.RSS),
        ],
    )

    orchestrator.run()

    assert failing_transcript_service.transcript_calls == 1
    assert video_validator.validate_calls == 0
    assert downloader.download_calls == 0

def test_validation_summarizes_video(
    fake_config: AppConfig,
    validate_vid: Video,
    transcript_service: FakeTranscriptService,
    downloader: FakeDownloader,
    summarizer: FakeSummarizer,
    video_db: VideoProcessingRepository,
    video_filter: FakeVideoFilter,
):
    validator = FakeValidator(decision="summarized")

    orchestrator = VidsiftOrchestrator(
        config=fake_config,
        video_validator=validator,
        transcript_service=transcript_service,
        summarizer=summarizer,
        downloader=downloader,
        video_db=video_db,
        video_filter=video_filter,
        should_sleep=False,
    )

    orchestrator.video_data_collector = FakeDataCollector(
        channel_id_list=[validate_vid.channel_id],
        config=fake_config,
        videos=[(validate_vid, DiscoverySource.RSS)],
    )

    orchestrator.run()

    assert validator.validate_calls == 1
    assert transcript_service.transcript_calls == 1
    assert summarizer.summarize_calls == 1
    assert downloader.download_calls == 0

def test_validation_discards_video(
    fake_config: AppConfig,
    validate_vid: Video,
    transcript_service: FakeTranscriptService,
    downloader: FakeDownloader,
    summarizer: FakeSummarizer,
    video_db: VideoProcessingRepository,
    video_filter: FakeVideoFilter,
):
    validator = FakeValidator(decision="discarded")

    orchestrator = VidsiftOrchestrator(
        config=fake_config,
        video_validator=validator,
        transcript_service=transcript_service,
        summarizer=summarizer,
        downloader=downloader,
        video_db=video_db,
        video_filter=video_filter,
        should_sleep=False,
    )

    orchestrator.video_data_collector = FakeDataCollector(
        channel_id_list=[validate_vid.channel_id],
        config=fake_config,
        videos=[(validate_vid, DiscoverySource.RSS)],
    )

    orchestrator.run()

    assert validator.validate_calls == 1
    assert transcript_service.transcript_calls == 1
    assert summarizer.summarize_calls == 0
    assert downloader.download_calls == 0

def test_multiple_videos_take_independent_actions(
    fake_config: AppConfig,
    transcript_service: FakeTranscriptService,
    downloader: FakeDownloader,
    summarizer: FakeSummarizer,
    video_db: VideoProcessingRepository,
    video_filter: FakeVideoFilter,
    validate_vid: Video,
):
    validator = FakeValidator(
        decisions=[
            "downloaded",
            "summarized",
        ]
    )

    vid2 = Video(
        title="video2",
        url="url2",
        author="author",
        channel_id="UCo71RUe6DX4w-Vd47rFLXPg",
        published="today",
        video_id="22222222222",
    )

    orchestrator = VidsiftOrchestrator(
        config=fake_config,
        video_validator=validator,
        transcript_service=transcript_service,
        summarizer=summarizer,
        downloader=downloader,
        video_db=video_db,
        video_filter=video_filter,
        should_sleep=False,
    )

    orchestrator.video_data_collector = FakeDataCollector(
        channel_id_list=[validate_vid.channel_id],
        config=fake_config,
        videos=[
            (validate_vid, DiscoverySource.RSS),
            (vid2, DiscoverySource.RSS),
        ],
    )

    orchestrator.run()

    assert validator.validate_calls == 2
    assert transcript_service.transcript_calls == 2
    assert downloader.download_calls == 1
    assert summarizer.summarize_calls == 1
