from youtube_transcript_api import FetchedTranscript, YouTubeTranscriptApi
from youtube_transcript_api._errors import (CookieError, InvalidVideoId,
                                            IpBlocked, RequestBlocked,
                                            VideoUnavailable)

from errorprotocol import logger

log = logger()


class TranscriptExtractor:
    def __init__(self) -> None:
        self.transcript_api: YouTubeTranscriptApi = YouTubeTranscriptApi()
    def extract_transcript(self, video_id: str) -> str | None:
        try:
            fetched_transcript: FetchedTranscript = self.transcript_api.fetch(video_id=video_id)
        except CookieError as e:
            log.log_error(f"CookieError while extracting the transcript of video id {video_id}: {e}")
            return
        except InvalidVideoId as e:
            log.log_error(f"InvalidVideoId while extracting the transcript of video id {video_id}: {e}")
        except VideoUnavailable as e:
            log.log_error(f"VideoUnavailable Error while extracting the transcript of video id {video_id}: {e}")
        except IpBlocked as e:
            log.log_error(f"IPBlocked Error while extracting the transcript of video id {video_id}: {e}")
        except RequestBlocked as e:
            log.log_error(f"RequestBlocked Error while extracting the transcript of video id {video_id}: {e}")
        except Exception as e:
            log.log_error(f"Exception while extracting the transcript of video id {video_id}: {e}")
        else:
            full_transcript: list = []
            for snippet in fetched_transcript:
                full_transcript.append(snippet.text)
            return "\n".join(full_transcript)

if __name__ == "__main__":
    te = TranscriptExtractor()
    te.extract_transcript("G3jvn7n-68Y")

