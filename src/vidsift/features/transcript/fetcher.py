from typing import Any

# for the youtube_transcript_api backend
from youtube_transcript_api import FetchedTranscript, YouTubeTranscriptApi
from youtube_transcript_api._errors import (CookieError, InvalidVideoId,
                                            IpBlocked, RequestBlocked,
                                            VideoUnavailable)
# for the yt-dlp backend
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadCancelled, DownloadError

from vidsift.features.transcript.errors import (TranscriptDownloadError,
                                                TranscriptError,
                                                TranscriptFetchingBlockedError,
                                                TranscriptFetchingError,
                                                TranscriptNotAvailibleError)


class TranscriptFetcher:
    def __init__(self) -> None:
        self.transcript_api: YouTubeTranscriptApi = YouTubeTranscriptApi()
    def extract_transcript(self, video_id: str) -> str:
        try:
            fetched_transcript: FetchedTranscript = self.transcript_api.fetch(video_id=video_id)
        except CookieError as e:
            raise TranscriptFetchingError(str(e))
        except InvalidVideoId as e:
            raise TranscriptNotAvailibleError(str(e))
        except VideoUnavailable as e:
            raise TranscriptNotAvailibleError(str(e))
        except IpBlocked as e:
            raise TranscriptFetchingBlockedError(str(e))
        except RequestBlocked as e:
            raise TranscriptFetchingBlockedError(str(e))
        except Exception as e:
            raise TranscriptError(str(e))
        else:
            full_transcript: list = []
            for snippet in fetched_transcript:
                full_transcript.append(snippet.text)
            return "\n".join(full_transcript)
 
    def extract_transcript_yt_dlp(self, video_url: str) -> None:
        ydl_opts: dict[str, Any] = {
            "writeautomaticsub": True,
            "writesubtitles": True,
            "subtitlesformat": "vtt",
            "cookiesfrombrowser": tuple(["firefox"]),
            "skip_download": True,
            "sleep_interval_requests": 3,
            "outtmpl": "/tmp/%(id)s.%(lang)s.%(ext)s",
            "remote-components": "ejs/github",
            #"extractor_args": {
            #    "youtube": {
            #        "player_client": ["android"]
            #    }
            #}
        }
        with YoutubeDL(ydl_opts) as ydl: 
            try:
                ydl.extract_info(video_url, download=True)
            except DownloadError as e:
                raise TranscriptDownloadError(str(e))
            except DownloadCancelled as e:
                raise TranscriptDownloadError(str(e))
            except Exception as e:
                raise TranscriptError(str(e))

if __name__ == "__main__":
    tf: TranscriptFetcher = TranscriptFetcher()
    tf.extract_transcript_yt_dlp(video_url="https://www.youtube.com/watch?v=scEDHsr3APg")

