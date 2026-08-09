import logging
from typing import Literal

from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import VideoFilteringError
from vidsift.models.video import Video

logger = logging.getLogger(__name__)


class VideoFilter:
    def __init__(self, config: AppConfig) -> None:
        yt_dlp_config = config.video_processing.yt_dlp
        ytl_opts = {
            "cookiesfrombrowser": tuple([yt_dlp_config.base.cookies_from_browser]),
            "sleep_interval_requests": yt_dlp_config.base.sleep_requests,
            "quiet": yt_dlp_config.base.quiet,
            "extract_flat": True,
        }
        self.ydl = YoutubeDL(ytl_opts)

    def _extract_data(self, vid: Video):
        try:
            return self.ydl.extract_info(vid.url, download=False)
        except Exception as e:
            raise VideoFilteringError(
                f"Error while checking if video is livestream: {e}"
            )

    def run_filters(
        self, vid: Video
    ) -> tuple[bool, Literal["livestream", "members-only"] | None]:
        """
        Method for running all of the filters.
        Each filter method starts with _check and returns a bool.
        If the bool is True, it means that the video passed the filter.
        If the bool is False, it means it didn't pass the filter.
        For doing that, it fetches once
        Return:
            - If one filter does not get passed, it returns `False, <filter_name>` on which it failed
            - If it passes all of the filters, it returns `True, None`
        """

        data = self._extract_data(vid)
        filters = {
            "members-only": self._check_member_only,
            "livestream": self._check_is_livestream,  # livestream checks at the end cause it might fail
        }
        for filter, runner in filters.items():
            result = runner(vid, data)
            if result is False:
                logger.debug(
                    f"Finished running filters on video '{vid.video_id}'. It won't be processed because it seems to be {filter}",
                    extra={
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                        "passed_filters": False,
                        "live_status": data.get("live_status"),
                        "was_live": data.get("was_live"),
                        "release_timestamp": data.get("release_timestamp"),
                        "availibility": data.get("availability"),
                    },
                )
                return False, filter
        logger.debug(
            f"Finished running filters on video '{vid.video_id}'. It will be processed.",
            extra={
                "video_id": vid.video_id,
                "channel_id": vid.channel_id,
                "passed_filters": True,
                "live_status": data.get("live_status"),
                "was_live": data.get("was_live"),
                "release_timestamp": data.get("release_timestamp"),
                "availibility": data.get("availability"),
            },
        )
        return True, None

    def _check_member_only(self, vid: Video, data: dict) -> bool:
        """
        Returns True if it is not members-only content, False if it is
        """
        availibility = data.get("availibility")
        if availibility == "subscriber_only":
            return False
        return True

    def _check_is_livestream(self, vid: Video, data) -> bool:
        """
        Returns False if it is a livestream, True if not
        """
        live_status = data.get("live_status")
        if live_status == "not_live":
            return True
        return False
