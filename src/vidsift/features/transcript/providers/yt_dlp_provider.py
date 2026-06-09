import logging
import re
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadCancelled, DownloadError

from vidsift.features.transcript.errors import (TranscriptDownloadError,
                                                TranscriptError,
                                                TranscriptNotFoundError,
                                                VTTFileReadingError)
from vidsift.features.transcript.providers.base import TranscriptProvider
from vidsift.models.video import Video

logger = logging.getLogger(__name__)

class YtDlpTranscriptProvider(TranscriptProvider):
    def __init__(self) -> None:
        super().__init__()
        Path("/tmp/vidsift/").mkdir(exist_ok=True, parents=True)

    def fetch_transcript(self, video_url: str) -> None:
        """
            Writes transcript vtt to a file under /tmp/
            Returns:
            - None
            Raises:
            - TranscriptDownloadError
            - TranscriptError
        """
        ydl_opts: dict[str, Any] = {
            "writeautomaticsub": True,
            "writesubtitles": True,
            "subtitlesformat": "vtt",
            "cookiesfrombrowser": tuple(["firefox"]),
            "skip_download": True,
            "sleep_interval_requests": 3,
            "outtmpl": "/tmp/vidsift/%(id)s.%(lang)s.%(ext)s",
            "remote-components": "ejs/github",
            #"extractor_args": {
            #    "youtube": {
            #        "player_client": ["android"]
            #    }
            #}
        }
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.extract_info(video_url, download=True)
            except DownloadError as e:
                raise TranscriptDownloadError(str(e))
            except DownloadCancelled as e:
                raise TranscriptDownloadError(str(e))
            except Exception as e:
                raise TranscriptError(str(e))

    def find_vtt_file(self, video_id: str) -> Path:
        """
        Method to get the path of the vtt transcript file
        Returns the Path
        If it is nonexistent, it raises a TranscriptNotFoundError.
        """
        for tmp_file in Path("/tmp/vidsift/").iterdir():
            if Path(tmp_file).is_file():
                if str(Path(tmp_file)).endswith(".vtt"):
                    if str(Path(tmp_file).name).startswith(video_id):
                        return tmp_file
        raise TranscriptNotFoundError(f"No .vtt transcript file got found under /tmp/vidsift/ with the video id {video_id}")

    def convert_vtt_to_str(self, vtt_file: Path):
        """
            Method to convert a .vtt file to a transcript string
            Raises:
            - TranscriptNotFoundError if the transcript file was not found
            - VTTFileReadingError if there were permissions missing to read the file
        """
        try:
            with open(vtt_file) as file:
                vtt_content = file.read()
        except FileNotFoundError:
            raise TranscriptNotFoundError(f"No .vtt transcript found under {str(vtt_file)}")
        except PermissionError:
            raise VTTFileReadingError(f"Reading permissions are missing for {str(vtt_file)}")
        else:
            vtt_content_list: list[str] = vtt_content.splitlines()
            transcipt: list[str] = []
            for line in vtt_content_list:
                if "-->" in line:
                    continue
                if line == "":
                    continue
                if "WEBVTT" == line or "Kind: captions" == line or "Language: en" == line:
                    continue
                line = re.sub(r"<[^>]+>", "", line)
                try:
                    if line == transcipt[-1]:
                        continue
                except IndexError:
                    pass
                transcipt.append(line)
            return " ".join(transcipt)

    def get_transcript(self, video: Video) -> str:
        """
            Method to get the transcript as a string
            Raises:
            - TranscriptError on failure
        """
        try:
            logger.debug(f"Fetching the transcript of video with id {video.video_id} with provider yt-dlp...")
            self.fetch_transcript(video.url)
            logger.debug(f"Parsing the .vtt transcript file of video id {video.video_id} to a string...")
            return self.convert_vtt_to_str(vtt_file=self.find_vtt_file(video_id=video.video_id))
        except TranscriptNotFoundError as e:
            logger.warning(f"TranscriptNotFoundError: {str(e)}")
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with yt-dlp")
        except TranscriptDownloadError as e:
            logger.warning(f"TranscriptDownloadError: Failed to download the transcript of {video.video_id}: {str(e)}")
            raise TranscriptError(f"Failed to get the transcript of {video.video_id} with yt-dlp")
        except VTTFileReadingError as e:
            logger.warning(f"VTTFileReadingError: Failed to read .vtt file of transcript of {video.video_id}: {str(e)}")
            raise TranscriptError(f"TranscriptError: Failed to download the transcript of {video.video_id}: {str(e)}")
        except TranscriptError as e:
            logger.warning(f"TranscriptError: Failed to fetch and download the transcript of {video.video_id}: {str(e)}")
            raise TranscriptError(f"TranscriptError: Failed to download the transcript of {video.video_id}: {str(e)}")
        except Exception as e:
            logger.warning(f"Exception: Failed to fetch and download the transcript of {video.video_id}: {str(e)}")
            raise TranscriptError(f"TranscriptError: Failed to download the transcript of {video.video_id}: {str(e)}")

    def get_provider_name(self) -> str:
        return "yt_dlp"
