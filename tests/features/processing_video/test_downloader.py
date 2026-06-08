import pytest

from tests.fakes.fake_pipeline import (FakeDownloader, FakeSummarizer,
                                       FakeTranscriptService, FakeValidator)
from vidsift.features.video_cache.repository import VideoCacheRepository
from vidsift.models.video import Video
from vidsift.models.video_cache_model import ProcessingStatus
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator


@pytest.fixture()
def set_up_validator():
    return FakeValidator(decision="downloaded")
@pytest.fixture()
def set_up_transcript_service():
    return FakeTranscriptService()
@pytest.fixture()
def set_up_downloader():
    return FakeDownloader()
@pytest.fixture()
def set_up_db(tmp_path):
    return VideoCacheRepository(db_path=tmp_path / "test.db")
@pytest.fixture()
def set_up_summarizer():
    return FakeSummarizer()

vid: Video = Video("sometitle", "someurl", "someauthor", "somechannelid", "somepubdate", "uuuuuuuuuuu")

def test_download_video_marks_done(set_up_db, set_up_validator, set_up_downloader, set_up_transcript_service, set_up_summarizer):
    validator = set_up_validator
    downloader: FakeDownloader = set_up_downloader
    summarizer: FakeSummarizer = set_up_summarizer
    transcript_service = set_up_transcript_service
    db: VideoCacheRepository = set_up_db

    orchestrator = VidsiftOrchestrator(
            channel_id_list=["somechannelid"],
            video_validator=validator,
            transcript_service=transcript_service,
            downloader=downloader,
            video_db=db
        )
    orchestrator.process_validation_pipeline(vid=vid, create_db_entry=True)
    assert downloader.was_called is True
    assert summarizer.was_called is False

    cached = db.get(vid.video_id)
    assert cached is not None
    assert cached.decision == "downloaded"
    assert cached.status == ProcessingStatus.DONE


def test_summary(set_up_db, set_up_transcript_service,  set_up_summarizer, set_up_downloader):
    validator: FakeValidator = FakeValidator(decision="summarized")
    transcript_service: FakeTranscriptService = set_up_transcript_service
    db: VideoCacheRepository = set_up_db
    summarizer: FakeSummarizer = set_up_summarizer
    downloader: FakeDownloader = set_up_downloader
    orchestrator = VidsiftOrchestrator(
        channel_id_list=["somechannelid"],
        video_validator=validator,
        summarizer=set_up_summarizer,
        video_db=db,
        transcript_service=transcript_service
    )
    orchestrator.process_validation_pipeline(vid=vid, create_db_entry=True)

    assert summarizer.was_called is True
    assert not downloader.was_called
    cached = db.get(vid.video_id)
    assert cached is not None
    assert cached.decision == "summarized"
    assert cached.status == ProcessingStatus.DONE

def test_discard(set_up_db, set_up_summarizer, set_up_downloader, set_up_transcript_service):
    validator: FakeValidator = FakeValidator(decision="discarded")
    summarizer: FakeSummarizer = set_up_summarizer
    downloader: FakeDownloader = set_up_downloader
    transcript_service: FakeTranscriptService = set_up_transcript_service
    db: VideoCacheRepository = set_up_db
    orchestrator = VidsiftOrchestrator(
        channel_id_list=["somechannelid"],
        video_db=db,
        video_validator=validator,
        summarizer=summarizer,
        downloader=downloader,
        transcript_service=transcript_service
    )
    orchestrator.process_validation_pipeline(vid=vid, create_db_entry=True)

    assert not summarizer.was_called
    assert not downloader.was_called
    cached = db.get(vid.video_id)
    assert cached is not None
    assert cached.decision == "discarded"
    assert cached.status == ProcessingStatus.DONE




