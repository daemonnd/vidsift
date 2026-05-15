from pathlib import Path

from .transcript_fetcher import TranscriptFetcher
from .utils.errorprotocol import logger
from .utils.transcript_helper.vtt_transcript_extractor import \
    VTTranscriptExtractor
from .utils.video_id_extractor import VideoIDExtractor

log: logger = logger()
transcript_parser: VTTranscriptExtractor = VTTranscriptExtractor()
transcript_fetcher: TranscriptFetcher = TranscriptFetcher()
video_id_extractor: VideoIDExtractor = VideoIDExtractor()

URL="https://www.youtube.com/watch?v=CinPOlgq0kQ"
transcript_fetcher.extract_transcript_yt_dlp(URL)
file: Path = transcript_parser.find_vtt_file(video_id_extractor.extract_id(URL))
print(str(file))
print(transcript_parser.convert_vtt_to_str(vtt_file=file))

