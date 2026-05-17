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
from vidsift.shared.errorprotocol import logger

log = logger()


class TranscriptFetcher:
    def __init__(self) -> None:
        self.transcript_api: YouTubeTranscriptApi = YouTubeTranscriptApi()
    def extract_transcript(self, video_id: str) -> str:
        try:
            fetched_transcript: FetchedTranscript = self.transcript_api.fetch(video_id=video_id)
        except CookieError as e:
            log.log_error(f"CookieError while extracting the transcript of video id {video_id}: {e}")
            raise TranscriptFetchingError(str(e))
        except InvalidVideoId as e:
            log.log_error(f"InvalidVideoId while extracting the transcript of video id {video_id}: {e}")
            raise TranscriptNotAvailibleError(str(e))
        except VideoUnavailable as e:
            log.log_error(f"VideoUnavailable Error while extracting the transcript of video id {video_id}: {e}")
            raise TranscriptNotAvailibleError(str(e))
        except IpBlocked as e:
            log.log_error(f"IPBlocked Error while extracting the transcript of video id {video_id}: {e}")
            raise TranscriptFetchingBlockedError(str(e))
        except RequestBlocked as e:
            log.log_error(f"RequestBlocked Error while extracting the transcript of video id {video_id}: {e}")
            raise TranscriptFetchingBlockedError(str(e))
        except Exception as e:
            log.log_error(f"Exception while extracting the transcript of video id {video_id}: {e}")
            raise TranscriptError(str(e))
        else:
            full_transcript: list = []
            for snippet in fetched_transcript:
                full_transcript.append(snippet.text)
            return "\n".join(full_transcript)
 
    def extract_transcript_yt_dlp(self, video_url: str) -> None:
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitlesformat": "vtt",
            "skip_download": True,
            "sleep_requests": 3,
            "outtmpl": "/tmp/%(id)s.%(lang)s.%(ext)s",
        }
        with YoutubeDL(ydl_opts) as ydl: # type: ignore
            try:
                ydl.extract_info(video_url, download=True)
            except DownloadError as e:
                log.log_error(f"DownloadError: The transcript of {video_url} could not be downloaded: {e}")
                raise TranscriptDownloadError(str(e))
            except DownloadCancelled as e:
                log.log_warning(f"DownloadCancelled: The transcript of {video_url} could not be downloaded, it got cancelled: {e}")
                raise TranscriptDownloadError(str(e))
            except Exception as e:
                log.log_warning(f"Exception: The transcript of {video_url} could not be downloaded: {e}")






