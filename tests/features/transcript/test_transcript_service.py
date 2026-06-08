import pytest

from vidsift.models.video import Video
from vidsift.services.transcript_service import TranscriptService


@pytest.fixture
def set_up_transcript_service():
    return TranscriptService()
#def test_extract_transcript_yt_dlp(set_up_transcript_service):
#    transcript_service: TranscriptService = set_up_transcript_service
#
#    assert isinstance(transcript_service.get_transcript(
#        video=Video(
#            url="https://www.youtube.com/watch?v=rAzT5lcezPs", author="", video_id="", title="", published="", channel_id=""
#        )
#    ), str)



