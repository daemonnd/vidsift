from pathlib import Path

import pytest

from vidsift.features.validation.transcript_validator.transcript_chunk_provider import \
    TranscriptChunkProvider


@pytest.fixture()
def set_up_transcript_chunk_provider():
    return TranscriptChunkProvider(char_chunk_size=500)

# f = fake transcript
# r = real transcript

fshort_transcript: str = "This is a short transcript. It should be chunked into one chunk only."
fmedium_transcript: str = "This is a medium transcript. It should be chunked into two chunks only. " * 10
flarge_transcript: str = "This is a large transcript. It should be chunked into multiple chunks. " * 100

with open(file="test_data/test_transcript1.txt", mode="r") as f:
    rregular_transcript1: str = f.read()
with open(file="test_data/test_transcript2.txt", mode="r") as f:
    rregular_transcript2: str = f.read()
with open(file="test_data/test_transcript3.txt", mode="r") as f:
    rlong_transcript: str = f.read()
with open(file="test_data/test_transcript4.txt", mode="r") as f:
    rshort_transcript: str = f.read()


def test_get_necessary_chunks_short_transcript(set_up_transcript_chunk_provider):
    provider = set_up_transcript_chunk_provider

    # short transcripts
    assert provider.get_necessary_chunks(fshort_transcript) == """First Chunks:
This is a short transcript. It should be chunked into one chunk only.


Last Chunks:

"""

    assert provider.get_necessary_chunks(rshort_transcript).strip() == Path("test_data/expected_rtranscript4.txt").read_text().strip()

    # medium transcripts
    assert provider.get_necessary_chunks(fmedium_transcript).strip() == Path("test_data/expected_ftranscript2.txt").read_text().strip()

    assert provider.get_necessary_chunks(rregular_transcript1).strip() == Path("test_data/expected_rtranscript1.txt").read_text().strip()
    assert provider.get_necessary_chunks(rregular_transcript2).strip() == Path("test_data/expected_rtranscript2.txt").read_text().strip()

    # large transcripts
    assert provider.get_necessary_chunks(flarge_transcript).strip() == Path("test_data/expected_ftranscript3.txt").read_text().strip()
    assert provider.get_necessary_chunks(rlong_transcript).strip() == Path("test_data/expected_rtranscript3.txt").read_text().strip()
