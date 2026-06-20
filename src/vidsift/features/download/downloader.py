from pathlib import Path

from yt_dlp import YoutubeDL

from vidsift.features.download.errors import VideoDownloadError


class VideoDownloader:
    def __init__(self):

        self.ydl_opts = {
            "format": "best",
            "cookiesfrombrowser": tuple(["firefox"]),
            "sleep_interval_requests": 3,
        }

    def download(self, video_url: str, output_path: Path) -> None:
        try:
            download_opts = self.ydl_opts
            download_opts["outtmpl"] = str(Path(output_path / "%(title)s.%(ext)s"))
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            raise VideoDownloadError(str(e)) from e
        except BaseException:
            raise

if __name__ == "__main__":
    vd: VideoDownloader = VideoDownloader()
    vd.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ", output_path=Path("/home/user/Videos/vidsift/"))

