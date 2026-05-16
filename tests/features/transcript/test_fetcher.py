import pytest

from vidsift.features.transcript.fetcher import TranscriptFetcher


@pytest.fixture
def set_up_fetcher():
    return TranscriptFetcher()
def test_extract_transcript_yt_dlp(set_up_fetcher):
    assert set_up_fetcher.extract_transcript_yt_dlp("https://www.youtube.com/watch?v=FEex8E1yDj4") is None
def test_extract_transcript(set_up_fetcher):
    assert type(set_up_fetcher.extract_transcript("UtMMjXOlRQc")) is str
