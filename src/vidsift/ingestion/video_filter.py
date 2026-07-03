from yt_dlp import YoutubeDL

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import VideoFilteringError
from vidsift.models.video import Video


class VideoFilter:
    def __init__(self, config: AppConfig) -> None:
        yt_dlp_config = config.video_processing.yt_dlp
        self.ytl_opts = {
            "cookies_from_browser": tuple([yt_dlp_config.cookies_from_browser]),
            "sleep_interval_requests": yt_dlp_config.sleep_requests,
            "quiet": yt_dlp_config.quiet,
        }
    def check_is_livestream(self, vid: Video) -> bool:
        """
        Returns True if it is a livestream, False if not
        """
        try:
            with YoutubeDL(self.ytl_opts) as ydl:
                data = ydl.extract_info(vid.url, download=False)
        except Exception as e:
            raise VideoFilteringError(f"Error while checking if video is livestream: {e}")
        else:
            live_status = data.get("live_status")
            print(f"live status of vid '{vid.video_id}': '{live_status}'")
            if live_status == "not_live":
                return False
            return True
if __name__ == "__main__":
    vf = VideoFilter()
    vid=Video(title="", url="https://www.youtube.com/watch?v=rAzT5lcezPs", author="pewds", channel_id="UC5UAwBUum7CPN5buc-_N1Fw", published="", video_id="rAzT5lcezPs")
    print(vf.check_is_livestream(vid=vid))
    vid=Video(title="", url="https://www.youtube.com/watch?v=eG1GVxrrHt8", author="pewds", channel_id="UC5UAwBUum7CPN5buc-_N1Fw", published="", video_id="rAzT5lcezPs")
    print(vf.check_is_livestream(vid=vid))
