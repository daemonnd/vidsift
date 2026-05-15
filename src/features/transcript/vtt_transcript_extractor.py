import re
from pathlib import Path

from src.models import video

from ...shared.errorprotocol import logger
from .errors import TranscriptNotFoundError, VTTFileReadingError

log = logger()


class VTTranscriptExtractor:
    def find_vtt_file(self, video_id: str) -> Path:
        """
        Method to get the path of the vtt transcript file
        Returns the Path
        If it is nonexistent, it raises a FileNotFoundError.
        """
        for tmp_file in Path("/tmp").iterdir():
            if Path(tmp_file).is_file():
                if str(Path(tmp_file)).endswith(".vtt"):
                    if str(Path(tmp_file).name).startswith(video_id):
                        return tmp_file
        raise TranscriptNotFoundError(f"No .vtt transcript file got found under /tmp/ with the video id {video_id}")


    def convert_vtt_to_str(self, vtt_file: Path):
        try:
            with open(vtt_file) as file:
                vtt_content = file.read()
        except FileNotFoundError:
            log.log_error(f"No file found at {str(vtt_file)}.")
            raise TranscriptNotFoundError(f"No .vtt transcript found under /tmp/ with the video id {video_id}")
        except PermissionError:
            log.log_error(f"Reading permissions are missing for {str(vtt_file)}.")
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
