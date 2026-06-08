import pytest

from tests.fake_files.fake_pipeline import (FakeDownloader,
                                            FakeTranscriptService,
                                            FakeValidator)
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


def test_download_video_marks_done(set_up_db, set_up_validator, set_up_downloader, set_up_transcript_service):
    validator = set_up_validator
    downloader: FakeDownloader = set_up_downloader
    transcript_service = set_up_transcript_service
    db: VideoCacheRepository = set_up_db

    orchestrator = VidsiftOrchestrator(
            channel_id_list=["somechannelid"],
            video_validator=validator,
            transcript_service=transcript_service,
            downloader=downloader,
            video_db=db
        )
    vid: Video = Video("sometitle", "someurl", "someauthor", "somechannelid", "somepubdate", "uuuuuuuuuuu")
    orchestrator.process_validation_pipeline(vid=vid, create_db_entry=True)
    assert downloader.was_called

    cached = db.get(vid.video_id)
    assert cached is not None
    assert cached.decision == "downloaded"
    assert cached.status == ProcessingStatus.DONE.value

