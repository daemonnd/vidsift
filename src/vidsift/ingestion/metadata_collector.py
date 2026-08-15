import logging
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import MetadataCollectionError
from vidsift.models.video import InvalidVideoError, Video
from vidsift.shared.config_helpers import get_js_runtimes_config
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.video_id_extractor import VideoIDExtractor

logger = logging.getLogger(__name__)


class MetadataCollector:
    def __init__(self, config: AppConfig) -> None:
        yt_dlp_config = config.video_processing.yt_dlp
        self.video_id_extractor = VideoIDExtractor()
        ydl_opts: dict[str, Any] = {
            "cookiesfrombrowser": tuple([yt_dlp_config.base.cookies_from_browser]),
            "skip_download": True,
            "sleep_interval_requests": yt_dlp_config.base.sleep_requests,
            "noplaylist": True,
            "quiet": yt_dlp_config.base.quiet,
            "js_runtimes": get_js_runtimes_config(yt_dlp_config.base.js_runtimes),
        }
        self.ydl: YoutubeDL = YoutubeDL(ydl_opts)

    def fetch_metadata(self, url: str):
        logger.info(
            f"Starting to fetch metadata for video with url {url}",
            extra={"event": LogEvent.METADATA_FETCH_STARTED, "url": url},
        )
        try:
            data = self.ydl.extract_info(
                url=url,
                download=False,
            )
        except DownloadError as e:
            logger.exception(
                f"DownloadError: Failed to fetch the data: {str(e)}",
                extra={
                    "event": LogEvent.METADATA_FETCH_FAILED,
                    "url": url,
                },
            )
            raise MetadataCollectionError(
                f"DownloadError: Failed to fetch the data: {str(e)}"
            ) from e
        except KeyError as e:
            logger.exception(
                f"KeyError: One of the required fields for creating a video object does not exist: {str(e)}",
                extra={
                    "event": LogEvent.METADATA_FETCH_FAILED,
                    "url": url,
                },
            )
            raise MetadataCollectionError(
                f"KeyError: One of the required fields for creating a video object does not exist: {str(e)}"
            ) from e
        else:
            try:
                to_return: dict[str, Any] = {
                    "title": data.get("title"),
                    "url": url,
                    "author": data.get("uploader"),
                    "channel_id": data["channel_id"],
                    "published": data.get("upload_date"),
                    "video_id": data["id"],
                    "duration": data.get("duration"),
                }
            except KeyError as e:
                logger.exception(
                    f"KeyError: One of the required fields for creating a video object does not exist: {str(e)}",
                    extra={
                        "event": LogEvent.METADATA_FETCH_FAILED,
                        "url": url,
                    },
                )
                raise MetadataCollectionError(
                    f"KeyError: One of the required fields for creating a video object does not exist: {str(e)}",
                ) from e

            else:
                logger.info(f"Metadata collection from url {url} completed.")
                try:
                    return Video(
                        title=to_return["title"],
                        url=to_return["url"],
                        author=to_return["author"],
                        channel_id=to_return["channel_id"],
                        published=to_return["published"],
                        video_id=to_return["video_id"],
                        duration=to_return["duration"]
                    )
                except InvalidVideoError:
                    raise
