import logging

from vidsift.config.models import AppConfig
from vidsift.features.transcript.errors import TranscriptError
from vidsift.features.transcript.providers.base import TranscriptProvider
from vidsift.features.transcript.providers.transcript_api_provider import \
    YoutubeTranscriptApiProvider
from vidsift.features.transcript.providers.yt_dlp_provider import \
    YtDlpTranscriptProvider
from vidsift.models.video import Video
from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)


class TranscriptService:
    def __init__(self, config: AppConfig) -> None:
        self.providers: list[TranscriptProvider] = [YtDlpTranscriptProvider(config=config), YoutubeTranscriptApiProvider()]

    def get_transcript(self, video: Video) -> str:
        for provider in self.providers:
            try:
                logger.info(
                    "Transcript fetching started.",
                    extra={
                        "event": LogEvent.TRANSCRIPT_FETCH_STARTED,
                        "video_id": video.video_id,
                        "channel_id": video.channel_id,
                        "provider": provider.get_provider_name(),
                    },
                )

                transcript = provider.get_transcript(video)

            except TranscriptError as e:
                logger.warning(
                    f"Transcript fetching failed with provider {provider.get_provider_name()}: {str(e)}",
                    extra={
                        "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                        "video_id": video.video_id,
                        "channel_id": video.channel_id,
                        "provider": provider.get_provider_name(),
                    },
                )

            except Exception as e:
                logger.warning(
                    f"Unexpected exception while fetching transcript with provider {provider.get_provider_name()}: {str(e)}",
                    extra={
                        "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                        "video_id": video.video_id,
                        "channel_id": video.channel_id,
                        "provider": provider.get_provider_name(),
                    },
                )
            except BaseException:
                raise
            else:
                logger.info(
                    f"Transcript fetching completed with provider {provider.get_provider_name()}",
                    extra={
                        "event": LogEvent.TRANSCRIPT_FETCH_COMPLETED,
                        "video_id": video.video_id,
                        "channel_id": video.channel_id,
                        "provider": provider.get_provider_name(),
                    },
                )

                return transcript


        # after the for loop, if all providers failed to fetch the transcript
        logger.error(
            "Transcript fetching failed with all providers.",
            extra={
                "event": LogEvent.TRANSCRIPT_FETCH_FAILED,
                "video_id": video.video_id,
                "channel_id": video.channel_id,
            },
        )

        raise TranscriptError("Failed to fetch the transcript with all providers")
