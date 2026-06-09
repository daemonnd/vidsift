import logging

from youtube_transcript_api import FetchedTranscript, YouTubeTranscriptApi
from youtube_transcript_api._errors import (CookieError, InvalidVideoId,
                                            IpBlocked, RequestBlocked,
                                            VideoUnavailable)

from vidsift.features.transcript.errors import (TranscriptError,
                                                TranscriptFetchingBlockedError,
                                                TranscriptFetchingError,
                                                TranscriptNotAvailibleError)
from vidsift.features.transcript.providers.base import TranscriptProvider
from vidsift.models.video import Video

logger = logging.getLogger(__name__)



class YoutubeTranscriptApiProvider(TranscriptProvider):
    def __init__(self) -> None:
        super().__init__()
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

    def get_transcript(self, video: Video) -> str:
        """
            Method to get the transcript as a string with youtube_transcript_api
            Raises:
            - TranscriptError
        """
        try:
            logger.debug(f"Fetching the transcript of video with id {video.video_id} with provider YouTube transcript API...")
            return self.extract_transcript_transcript_api(video_id=video.video_id)
        except TranscriptFetchingBlockedError as e:
            logger.warning(f"TranscriptFetchingBlockedError: {str(e)}")
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with YouTube transcript API")
        except InvalidVideoId as e:
            logger.warning(f"InvalidVideoId: {str(e)}")
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with YouTube transcript API")
        except TranscriptFetchingError as e:
            logger.warning(f"TranscriptFetchingError: {str(e)}")
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with YouTube transcript API")
        except TranscriptNotAvailibleError as e:
            logger.warning(f"TranscriptNotAvailibleError: {str(e)}")
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with YouTube transcript API")
        except TranscriptError as e:
            logger.warning(f"TranscriptError: Failed to fetch and download the transcript of {video.video_id}: {str(e)}")
            raise TranscriptError(f"TranscriptError: Failed to download the transcript of {video.video_id}: {str(e)}")
        except Exception as e:
            logger.warning(f"Exception: Failed to fetch and download the transcript of {video.video_id}: {str(e)}")
            raise TranscriptError(f"TranscriptError: Failed to download the transcript of {video.video_id}: {str(e)}")

    def get_provider_name(self) -> str:
        return "YouTube Transcript API"



