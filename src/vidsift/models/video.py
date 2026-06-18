from dataclasses import dataclass

from vidsift.models.video_record import VideoProcessingRecord

ALLOWED_VIDEO_ID_LENGTH: int = 11
ALLOWED_CHANNEL_ID_LENGTH: int = 24
ALLOWED_CHANNEL_ID_PREFIX: str = 'UC'

class InvalidVideoError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

@dataclass
class Video:
    title: str
    url: str
    author: str
    channel_id: str
    published: str
    video_id: str

    def __post_init__(self):
        if not isinstance(self.video_id, str):
            raise InvalidVideoError(f"The video id {self.video_id} is not a string, it is a {type(self.video_id)}")
        if not isinstance(self.channel_id, str):
            raise InvalidVideoError(f"The channel id {self.channel_id} is not a string, it is a {type(self.channel_id)}")
        if len(self.video_id) != ALLOWED_VIDEO_ID_LENGTH:
            raise InvalidVideoError(f"The video id {self.video_id} does not match the required length of 11, it is {len(self.video_id)}.")
        if len(self.channel_id) != ALLOWED_CHANNEL_ID_LENGTH:
            raise InvalidVideoError(f"The channel id {self.channel_id} does not match the required length of 24, it is {len(self.channel_id)}.")
        if not self.channel_id.startswith(ALLOWED_CHANNEL_ID_PREFIX):
            raise InvalidVideoError(f"The channel id {self.channel_id} does not start with 'UC'.")


    @classmethod
    def from_cache(cls, video_db_row: VideoProcessingRecord):
        return cls(
            title=video_db_row.title,
            url=video_db_row.url,
            author=video_db_row.author,
            channel_id=video_db_row.channel_id,
            published=video_db_row.published,
            video_id=video_db_row.video_id
        )
