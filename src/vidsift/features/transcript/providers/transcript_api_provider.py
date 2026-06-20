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
from vidsift.shared.logging.log_event_fields import LogEvent

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
        except BaseException:
            raise
        else:
            full_transcript: list = []
            for snippet in fetched_transcript:
                full_transcript.append(snippet.text)

            logger.debug(
                "Transcript fetched successfully.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_COMPLETED,
                    "video_id": video_id,
                    "transcript_snippet_count": len(full_transcript),
                },
            )

            return "\n".join(full_transcript)

    def get_transcript(self, video: Video) -> str:
        """
        Method to get the transcript as a string with youtube_transcript_api
        Raises:
        - TranscriptError
        """
        try:
            logger.info(
                "Transcript fetching started.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_STARTED,
                    "video_id": video.video_id,
                    "channel_id": video.channel_id,
                    "provider": self.get_provider_name(),
                },
            )

            transcript: str = self.extract_transcript_transcript_api(video_id=video.video_id)


        except TranscriptFetchingBlockedError as e:
            logger.warning(
                "Transcript fetching blocked.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                    "video_id": video.video_id,
                    "channel_id": video.channel_id,
                    "provider": self.get_provider_name(),
                    "error": str(e),
                },
            )
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with YouTube transcript API")
        except InvalidVideoId as e:
            logger.warning(
                "Invalid video ID while fetching transcript.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                    "video_id": video.video_id,
                    "channel_id": video.channel_id,
                    "provider": self.get_provider_name(),
                    "error": str(e),
                },
            )
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with YouTube transcript API")
        except TranscriptFetchingError as e:
            logger.warning(
                "Transcript fetching error occurred.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                    "video_id": video.video_id,
                    "channel_id": video.channel_id,
                    "provider": self.get_provider_name(),
                    "error": str(e),
                },
            )
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with YouTube transcript API")
        except TranscriptNotAvailibleError as e:
            logger.warning(
                "Transcript not available.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                    "video_id": video.video_id,
                    "channel_id": video.channel_id,
                    "provider": self.get_provider_name(),
                    "error": str(e),
                },
            )
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with YouTube transcript API")
        except TranscriptError as e:
            logger.warning(
                "Failed to fetch and download transcript.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                    "video_id": video.video_id,
                    "channel_id": video.channel_id,
                    "provider": self.get_provider_name(),
                    "error": str(e),
                },
            )
            raise TranscriptError(f"TranscriptError: Failed to download the transcript of {video.video_id}: {str(e)}")
        except Exception as e:
            logger.warning(
                "Unexpected exception while fetching and downloading transcript.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                    "video_id": video.video_id,
                    "channel_id": video.channel_id,
                    "provider": self.get_provider_name(),
                    "error": str(e),
                },
            )
            raise TranscriptError(f"TranscriptError: Failed to download the transcript of {video.video_id}: {str(e)}")
        except BaseException:
            raise
        else:
            logger.info(
                "Transcript fetching completed.",
                extra={
                    "event": LogEvent.TRANSCRIPT_FETCH_COMPLETED,
                    "video_id": video.video_id,
                    "channel_id": video.channel_id,
                    "provider": self.get_provider_name(),
                },
            )

            return transcript

    def get_provider_name(self) -> str:
        return "YouTube Transcript API"
