import pytest

from vidsift.models.video import Video
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator


@pytest.fixture
def basic_orchestrator():
    return VidsiftOrchestrator(["UCX6OQ3DkcsbYNE6H8uQQuVA", "UCV03SRZXJEz-hchIAogeJOg"])



def test_fetch_videos_without_channelids():
    with pytest.raises(ValueError) as excinfo:
        VidsiftOrchestrator([])
    assert str(excinfo.value) == "The channel ID list given for fetching video data is empty"

def test_fetch_videos(basic_orchestrator):
    videos: list[Video] = basic_orchestrator.fetch_videos()
    assert isinstance(videos, list)
    assert videos
    for v in videos:
        assert isinstance(v, Video)
        assert v
        assert isinstance(v.title, str)
        assert v.title
        assert isinstance(v.author, str)
        assert v.author
        assert isinstance(v.published, str)
        assert v.published
        assert isinstance(v.url, str)
        assert v.url
        assert isinstance(v.video_id, str)
        assert v.video_id


def test_fetch_videos_to_transcript(basic_orchestrator):
    videos: list[Video] = basic_orchestrator.fetch_videos()
    transcript: str = basic_orchestrator.fetch_and_download_transcript(video=videos[1])
    assert type(transcript) is str

