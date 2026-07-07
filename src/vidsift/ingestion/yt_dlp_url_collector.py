from typing import Generator

from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig, YtDlpBaseConfig
from vidsift.ingestion.errors import VideoDataCollectionError
from vidsift.models.video import Video


class YtDlpUrlCollector:
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        yt_dlp_config: YtDlpBaseConfig = config.video_processing.yt_dlp.base
        ydl_opts = {
            "cookiesfrombrowser": tuple([yt_dlp_config.cookies_from_browser]),
            "sleep_interval_requests": yt_dlp_config.sleep_requests,
            "quiet": yt_dlp_config.quiet,
            "max_retries": yt_dlp_config.max_retries,
            "playlist_items": f"1:{config.video_fetching.yt_dlp_video_amount}",
            "extract_flat": True,
            "sleep_interval": yt_dlp_config.sleep_requests
        }
        self.ydl: YoutubeDL = YoutubeDL(ydl_opts)

    def get_channel_url(self, channel_id: str) -> str:
        return f"https://www.youtube.com/channel/{channel_id}/videos" # only videos
    def parse_one_channel(self, channel_id: str) -> Generator[Video, None, None]:
        try:
            info = self.ydl.extract_info(
                url=self.get_channel_url(channel_id=channel_id),
                download=False,
            )
            for video in info["entries"]:
                vid =  Video(
                    title=str(video.get("title")),
                    url=f"https://www.youtube.com/watch?v={video.get("id")}",
                    author=str(video.get("uploader")),
                    published=str(video.get("upload_date")),
                    video_id=video.get("id"),
                    channel_id=channel_id
                )
                print(f"VIDEO: {vid}")
                yield vid
        except Exception as e:
            raise VideoDataCollectionError(str(e)) from e
        except BaseException:
            raise



