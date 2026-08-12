from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import IngestionEnrichmentError
from vidsift.models.video import Video
from vidsift.shared.config_helpers import get_js_runtimes_config


class IngestionEnrichment:
    def __init__(self, config: AppConfig) -> None:
        yt_dlp_config = config.video_processing.yt_dlp
        ytl_opts = {
            "cookiesfrombrowser": tuple([yt_dlp_config.base.cookies_from_browser]),
            "sleep_interval_requests": yt_dlp_config.base.sleep_requests,
            "quiet": yt_dlp_config.base.quiet,
            "js_runtimes": get_js_runtimes_config(yt_dlp_config.base.js_runtimes),
            "extract_flat": True,
        }
        self.ydl = YoutubeDL(ytl_opts)

    def entract_data(self, vid: Video):
        try:
            return self.ydl.extract_info(vid.url, download=False)
        except Exception as e:
            raise IngestionEnrichmentError(
                f"Error while fetching additional data for video: {e}"
            )
