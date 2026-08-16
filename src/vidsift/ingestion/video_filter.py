import logging
from typing import Literal

from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import VideoFilteringError
from vidsift.models.video import Video
from vidsift.shared.config_helpers import get_js_runtimes_config
from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)


class VideoFilter:
    def __init__(self, config: AppConfig) -> None:
        pass

    def run_filters(
        self, 
        vid: Video,
        data: dict | None = None, 
        error_message: str | None = None
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
        #if the method is not called correctly
        if data is None and error_message is None:
            raise ValueError("Either data or error_message must be provided")
        if data is not None and error_message is not None:
            raise ValueError("Only one of data or error_message can be provided")

        if data is not None:
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
        if error_message is not None:
            if "This live event will begin in" in str(error_message):
                if (
                    str(error_message).endswith("minutes.")
                    or str(error_message).endswith("hours.")
                    or str(error_message).endswith("days.")
                ):
                    logger.debug(
                        f"Finished running filters on video '{vid.video_id}'. It won't be processed because it seems to be a livestream",
                        extra={
                            "video_id": vid.video_id,
                            "channel_id": vid.channel_id,
                            "passed_filters": False,
                            "livestream": True,
                            "members_only": False
                        },
                    )
                    # if it is a livestream
                    return False, "livestream"

            elif "Join this channel to get access to members-only content like this video, and other exclusive perks." in str(error_message):
                logger.debug(
                    f"Finished running filters on video '{vid.video_id}'. It won't be processed because it seems to be members-only content",
                    extra={
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                        "passed_filters": False,
                        "livestream": False,
                        "members_only": True
                    },
                )
                # it is members-only content
                return False, "members-only"
            else:
                logger.debug(
                    f"Finished running filters on video '{vid.video_id}'. It will be processed.",
                    extra={
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id,
                        "passed_filters": True,
                        "livestream": False,
                        "members-only": False
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
