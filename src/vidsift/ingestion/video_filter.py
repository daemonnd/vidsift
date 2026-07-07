from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import VideoFilteringError
from vidsift.models.video import Video


class VideoFilter:
    def __init__(self, config: AppConfig) -> None:
        yt_dlp_config = config.video_processing.yt_dlp
        ytl_opts = {
            "cookiesfrombrowser": tuple([yt_dlp_config.base.cookies_from_browser]),
            "sleep_interval_requests": yt_dlp_config.base.sleep_requests,
            "quiet": yt_dlp_config.base.quiet,
            "extract_flat": True
        }
        self.ydl = YoutubeDL(ytl_opts)
    def check_is_livestream(self, vid: Video) -> bool:
        """
        Returns True if it is a livestream, False if not
        """
        try:
                data = self.ydl.extract_info(vid.url, download=False)
        except Exception as e:
            raise VideoFilteringError(f"Error while checking if video is livestream: {e}")
        else:
            live_status = data.get("live_status")
            if live_status == "not_live":
                return False
            return True
