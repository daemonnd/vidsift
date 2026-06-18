from pathlib import Path

import pytest

from vidsift.config.loader import load_config
from vidsift.models.video import Video
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator


@pytest.fixture()
def fake_config():
    return load_config(
        Path(f"{Path(__file__).parent.parent}/fakes/fake_config.toml")
    )

@pytest.fixture
def basic_orchestrator(fake_config):
    return VidsiftOrchestrator(
        channel_id_list=["UCX6OQ3DkcsbYNE6H8uQQuVA", "UCV03SRZXJEz-hchIAogeJOg"],
        config=fake_config
    )



def test_fetch_videos_without_channelids(fake_config):
    with pytest.raises(ValueError) as excinfo:
        VidsiftOrchestrator(
            channel_id_list=[],
            config=fake_config
        )
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

