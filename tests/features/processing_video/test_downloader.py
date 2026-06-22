
from pathlib import Path

import pytest

from tests.fakes.fake_pipeline import (FailingSummarizer,
                                       FailingTranscriptService,
                                       FakeDownloader, FakeSummarizer,
                                       FakeTranscriptService, FakeValidator)
from vidsift.config.loader import load_config
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.models.video import Video
from vidsift.models.video_record import (VideoProcessingRecord,
                                         VideoProcessingStatus)
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator


@pytest.fixture()
def validator():
    return FakeValidator(decision="downloaded")
@pytest.fixture()
def set_up_transcript_service():
    return FakeTranscriptService()
@pytest.fixture()
def vid_downloader():
    return FakeDownloader()
@pytest.fixture()
def summarization_service():
    return FakeSummarizer()
@pytest.fixture()
def vid():
    return Video("sometitle", "someurl", "someauthor", "UCjjjjjjjjjjjjjjjjjjjjjj", "somepubdate", "uuuuuuuuuuu")
@pytest.fixture()
def fake_config():
        return load_config(Path(f"{Path(__file__).parent.parent.parent}/fakes/fake_config.toml"))

@pytest.fixture()
def db(tmp_path, fake_config):
    return VideoProcessingRepository(db_path=tmp_path / "test.db", config=fake_config)
def test_download_video_marks_done(db, validator, vid_downloader, set_up_transcript_service, summarization_service, vid, fake_config):
    vid: Video = vid
    validator = validator
    downloader: FakeDownloader = vid_downloader
    summarizer: FakeSummarizer = summarization_service
    transcript_service = set_up_transcript_service
    db: VideoProcessingRepository = db

    orchestrator = VidsiftOrchestrator(
            should_sleep=False,
            video_validator=validator,
            transcript_service=transcript_service,
            downloader=downloader,
            video_db=db,
            config=fake_config
        )
    orchestrator.process_validation_pipeline(vid=vid, create_db_entry=True)
    assert downloader.was_called is True
    assert summarizer.was_called is False

    cached = db.get(vid.video_id)
    assert cached is not None
    assert cached.decision == "downloaded"
    assert cached.status == VideoProcessingStatus.DONE


def test_summary(db, set_up_transcript_service,  summarization_service, vid_downloader, vid, fake_config):
    vid: Video = vid
    validator: FakeValidator = FakeValidator(decision="summarized")
    transcript_service: FakeTranscriptService = set_up_transcript_service
    db: VideoProcessingRepository = db
    summarizer: FakeSummarizer = summarization_service
    downloader: FakeDownloader = vid_downloader
    orchestrator = VidsiftOrchestrator(
        should_sleep=False,
        video_validator=validator,
        summarizer=summarization_service,
        video_db=db,
        transcript_service=transcript_service,
        config=fake_config
    )
    orchestrator.process_validation_pipeline(vid=vid, create_db_entry=True)

    assert summarizer.was_called is True
    assert not downloader.was_called
    cached = db.get(vid.video_id)
    assert cached is not None
    assert cached.decision == "summarized"
    assert cached.status == VideoProcessingStatus.DONE

def test_discard(db, summarization_service, vid_downloader, set_up_transcript_service, vid, fake_config):
    vid: Video = vid
    validator: FakeValidator = FakeValidator(decision="discarded")
    summarizer: FakeSummarizer = summarization_service
    downloader: FakeDownloader = vid_downloader
    transcript_service: FakeTranscriptService = set_up_transcript_service
    db: VideoProcessingRepository = db
    orchestrator = VidsiftOrchestrator(
        should_sleep=False,
        video_db=db,
        video_validator=validator,
        summarizer=summarizer,
        downloader=downloader,
        transcript_service=transcript_service,
        config=fake_config
    )
    orchestrator.process_validation_pipeline(vid=vid, create_db_entry=True)

    assert not summarizer.was_called
    assert not downloader.was_called
    cached = db.get(vid.video_id)
    assert cached is not None
    assert cached.decision == "discarded"
    assert cached.status == VideoProcessingStatus.DONE

def test_failing_get_transcript(db, summarization_service, vid_downloader, vid, validator, fake_config):
    vid: Video = vid
    validator: FakeValidator = validator
    db: VideoProcessingRepository = db
    summarizer: FakeSummarizer = summarization_service
    downloader: FakeDownloader = vid_downloader
    transcript_service: FailingTranscriptService = FailingTranscriptService()

    orchestrator = VidsiftOrchestrator(
        should_sleep=False,
        video_db=db,
        video_validator=validator,
        summarizer=summarizer,
        downloader=downloader,
        transcript_service=transcript_service,
        config=fake_config
    )

    orchestrator.process_validation_pipeline(vid=vid, create_db_entry=True)

    assert not summarizer.was_called
    assert not downloader.was_called
    assert not validator.was_called
    cached = db.get(vid.video_id)
    assert cached is not None
    assert "TranscriptError" in cached.last_error
    assert cached.decision is None
    assert cached.status == VideoProcessingStatus.VALIDATING
    assert cached.retry_count > 0


def test_failing_validate_video(
    db,
    summarization_service,
    vid_downloader,
    vid,
    set_up_transcript_service,
    fake_config
):
    vid = vid
    validator = FakeValidator(
        decision="discarded",
        should_fail=True
    )

    db = db
    summarizer = summarization_service
    downloader = vid_downloader
    transcript_service = set_up_transcript_service

    orchestrator = VidsiftOrchestrator(
        should_sleep=False,
        video_db=db,
        video_validator=validator,
        summarizer=summarizer,
        downloader=downloader,
        transcript_service=transcript_service,
        config=fake_config
    )

    orchestrator.process_validation_pipeline(
        vid=vid,
        create_db_entry=True
    )

    assert validator.was_called
    assert not summarizer.was_called
    assert not downloader.was_called

    cached = db.get(vid.video_id)

    assert cached is not None
    assert cached.status == VideoProcessingStatus.VALIDATING
    assert cached.retry_count > 0
    assert cached.decision is None
    assert "VideoValidationError" in cached.last_error


def test_failing_summary(
    db,
    vid_downloader,
    vid,
    set_up_transcript_service,
    fake_config
):
    vid = vid

    validator = FakeValidator(
        decision="summarized"
    )

    summarizer = FailingSummarizer()

    downloader = vid_downloader
    transcript_service = set_up_transcript_service
    db = db

    orchestrator = VidsiftOrchestrator(
        should_sleep=False,
        video_db=db,
        video_validator=validator,
        summarizer=summarizer,
        downloader=downloader,
        transcript_service=transcript_service,
        config=fake_config
    )

    orchestrator.process_validation_pipeline(
        vid=vid,
        create_db_entry=True
    )

    assert validator.was_called
    assert summarizer.was_called
    assert not downloader.was_called

    cached: VideoProcessingRecord = db.get(vid.video_id)

    assert cached is not None
    assert cached.status == VideoProcessingStatus.SUMMARIZING
    assert cached.retry_count > 0

    # validation completed successfully
    assert cached.decision == "summarized"

    assert "SummaryError" in cached.last_error


def test_existing_video_is_skipped(
    db,
    vid,
    set_up_transcript_service,
    vid_downloader,
    summarization_service,
    fake_config
):
    vid = vid

    db = db
    db.create(vid)

    validator = FakeValidator(
        decision="downloaded"
    )

    transcript_service = set_up_transcript_service
    downloader = vid_downloader
    summarizer = summarization_service

    orchestrator = VidsiftOrchestrator(
        should_sleep=False,
        video_db=db,
        video_validator=validator,
        summarizer=summarizer,
        downloader=downloader,
        transcript_service=transcript_service,
        config=fake_config
    )

    orchestrator.process_validation_pipeline(
        vid=vid,
        create_db_entry=True
    )

    assert not validator.was_called
    assert not downloader.was_called
    assert not summarizer.was_called
