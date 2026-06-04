from yt_dlp import YoutubeDL


class VideoDownloader:
    def __init__(self):

        self.ydl_opts = {
            "format": "best",
            "cookiesfrombrowser": tuple(["firefox"]),
            "sleep_interval_requests": 3,
        }

    def download(self, video_url: str) -> None:
        with YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([video_url])

if __name__ == "__main__":
    vd: VideoDownloader = VideoDownloader()
    vd.download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

