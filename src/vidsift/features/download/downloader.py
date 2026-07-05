from pathlib import Path

from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig
from vidsift.features.download.errors import VideoDownloadError


class VideoDownloader:
    def __init__(self, config: AppConfig):
        yt_dlp_config = config.video_processing.yt_dlp

        self.ydl_opts = {
            "format": yt_dlp_config.download.format,
            "cookiesfrombrowser": tuple([yt_dlp_config.base.cookies_from_browser]),
            "sleep_interval_requests": yt_dlp_config.base.sleep_requests,
            "quiet": yt_dlp_config.base.quiet,
            "merge_output_format": yt_dlp_config.download.merge_output_format,
            "max_retries": yt_dlp_config.base.max_retries,
        }

    def download(self, video_url: str, output_path: Path) -> None:
        try:
            download_opts = self.ydl_opts
            download_opts["outtmpl"] = str(Path(output_path / "%(title)s [%(id)s].%(ext)s"))
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            raise VideoDownloadError(str(e)) from e
        except BaseException:
            raise
