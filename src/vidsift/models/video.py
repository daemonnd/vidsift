from dataclasses import dataclass

from vidsift.models.video_record import VideoProcessingRecord


@dataclass
class Video:
    title: str
    url: str
    author: str
    channel_id: str
    published: str
    video_id: str

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
