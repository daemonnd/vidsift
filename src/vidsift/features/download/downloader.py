from pathlib import Path

from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig
from vidsift.features.download.errors import (OutputPathIsADirectoryError,
                                              OutputPathNotFoundError,
                                              OutputPathPermissionError,
                                              VideoDownloadError)
from vidsift.models.video import InvalidVideoError
from vidsift.shared.config_helpers import get_js_runtimes_config


class VideoDownloader:
    def __init__(self, config: AppConfig):
        self.config = config
        if config.downloads.fake_download:
            self.download_config = config.downloads
        else:
            yt_dlp_config = config.video_processing.yt_dlp
            self.ydl_opts = {
                "format": yt_dlp_config.download.format,
                "cookiesfrombrowser": tuple([yt_dlp_config.base.cookies_from_browser]),
                "sleep_interval_requests": yt_dlp_config.base.sleep_requests,
                "quiet": yt_dlp_config.base.quiet,
                "js_runtimes": get_js_runtimes_config(yt_dlp_config.base.js_runtimes),
                "merge_output_format": yt_dlp_config.download.merge_output_format,
                "max_retries": yt_dlp_config.base.max_retries,
                "noplaylist": True,
            }

    def download(self, video_url: str, output_path: Path) -> None:
        if self.config.downloads.fake_download:
            self._fake_download(video_url)
        else:
            try:
                download_opts = self.ydl_opts
                download_opts["outtmpl"] = str(
                    Path(output_path / "%(title)s [%(id)s].%(ext)s")
                )
                with YoutubeDL(self.ydl_opts) as ydl:
                    ydl.download([video_url])
            except InvalidVideoError:
                raise
            except Exception as e:
                raise VideoDownloadError(str(e)) from e

    def _fake_download(self, video_url) -> None:
        try:
            with open(Path(self.download_config.output_path), "a") as f:
                f.write(video_url)
                f.write("\n")
        except PermissionError as e:
            raise OutputPathPermissionError(str(e)) from e
        except FileNotFoundError as e:
            raise OutputPathNotFoundError(str(e)) from e
        except IsADirectoryError as e:
            raise OutputPathIsADirectoryError(str(e)) from e

