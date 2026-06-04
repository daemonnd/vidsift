from pathlib import Path

from yt_dlp import YoutubeDL


class VideoDownloader:
    def __init__(self):

        self.ydl_opts = {
            "format": "best",
            "cookiesfrombrowser": tuple(["firefox"]),
            "sleep_interval_requests": 3,
        }

    def download(self, video_url: str, output_path: Path) -> None:
        self.ydl_opts["outtmpl"] = str(Path(f"{str(output_path)}/%(title)s.%(ext)s"))
        with YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([video_url])

if __name__ == "__main__":
    vd: VideoDownloader = VideoDownloader()
    vd.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ", output_path=Path("/home/user/Videos/vidsift/"))

