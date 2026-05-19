from pathlib import Path

import pytest

from vidsift.features.transcript.errors import TranscriptNotFoundError
from vidsift.features.transcript.vtt_transcripty_parser import \
    VTTranscriptParser


@pytest.fixture
def set_up_extractor():
    return VTTranscriptParser()

def test_convert_vtt_to_string(set_up_extractor):
    with pytest.raises(TranscriptNotFoundError) as excinfo:
        set_up_extractor.convert_vtt_to_str(Path("/tmp/aslödjöfasjdölfjasldfjasldfj.vtt"))
    assert str(excinfo.value) == "No .vtt transcript found under /tmp/aslödjöfasjdölfjasldfjasldfj.vtt"

