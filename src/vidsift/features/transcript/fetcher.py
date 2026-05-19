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
    def extract_transcript_transcript_api(self, video_id: str) -> str:
        """
            returns the fetched transcript as str or raises.
            Raises:
            - TranscriptFetchingError (CookieError)
            - InvalidVideoId
            - TranscriptNotAvailibleError
            - TranscriptFetchingBlockedError
            - TranscriptError
        """
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
 


