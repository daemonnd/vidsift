from typing import Generator

from yt_dlp import YoutubeDL

from vidsift.config.models import YtDlpBaseConfig
from vidsift.models.video import Video


class YtDlpUrlCollector:
    def __init__(self, config: YtDlpBaseConfig) -> None:
        super().__init__()
        yt_dlp_config: YtDlpBaseConfig = config
        self.ydl_opts = {
            "cookiesfrombrowser": tuple([yt_dlp_config.cookies_from_browser]),
            "sleep_interval_requests": yt_dlp_config.sleep_requests,
            "quiet": yt_dlp_config.quiet,
            "max_retries": yt_dlp_config.max_retries,
        }

    def get_channel_url(self, channel_id: str) -> str:
        return f"https://www.youtube.com/channel/{channel_id}/videos" # only videos
    def parse_one_channel(self, channel_id: str) -> Generator[Video, None, None]:
        with YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(
                url=self.get_channel_url(channel_id=channel_id),
                download=False,
            )
            for video in info["entries"]:
                yield Video(
                    title=video.get("title"),
                    url=video.get("url"),
                    author=video.get("uploader"),
                    published=video.get("upload_date"),
                    video_id=video["id"], # should raise if it is not there, it is strictly required
                    channel_id=video["channel_id"] # same as for video id
                )


