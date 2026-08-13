from typing import Generator

from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig, ChannelConfig, YtDlpBaseConfig
from vidsift.ingestion.errors import VideoDataCollectionError
from vidsift.models.video import InvalidVideoError, Video
from vidsift.shared.config_helpers import get_js_runtimes_config


class YtDlpUrlCollector:
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config: AppConfig = config
        yt_dlp_config: YtDlpBaseConfig = config.video_processing.yt_dlp.base
        ydl_opts = {
            "cookiesfrombrowser": tuple([yt_dlp_config.cookies_from_browser]),
            "sleep_interval_requests": yt_dlp_config.sleep_requests,
            "quiet": yt_dlp_config.quiet,
            "js_runtimes": get_js_runtimes_config(yt_dlp_config.js_runtimes),
            "max_retries": yt_dlp_config.max_retries,
            "playlist_items": f"1:{config.video_fetching.yt_dlp_video_amount}",
            "extract_flat": True,
            "sleep_interval": yt_dlp_config.sleep_requests,
        }
        self.ydl: YoutubeDL = YoutubeDL(ydl_opts)
        self.channel_lookup: dict = {}
        channels: list[ChannelConfig] = self.config.channels
        self.channel_lookup = {channel.id: channel for channel in channels}

    def get_channel_url(self, channel_id: str) -> str:
        return f"https://www.youtube.com/channel/{channel_id}/videos"  # only videos

    def parse_one_channel(self, channel_id: str) -> Generator[Video, None, None]:
        try:
            info = self.ydl.extract_info(
                url=self.get_channel_url(channel_id=channel_id),
                download=False,
            )
            for video in info["entries"]:
                vid = Video(
                    title=str(video.get("title")),
                    url=f"https://www.youtube.com/watch?v={video.get('id')}",
                    author=str(),  # self.channel_lookup.get(""),
                    published=str(video.get("upload_date")),
                    video_id=video.get("id"),
                    channel_id=channel_id,
                    duration=video.get("duration")
                )
                yield vid
        except InvalidVideoError:
            raise
        except Exception as e:
            raise VideoDataCollectionError(str(e)) from e
