from dataclasses import dataclass

from vidsift.models.video_cache_model import VideoCacheModel


@dataclass
class Video:
    title: str
    url: str
    author: str
    channel_id: str
    published: str
    video_id: str

    @classmethod
    def from_cache(cls, video_db_row: VideoCacheModel):
        return cls(
            title=cache.title,
            url=cache.url,
            author=cache.author,
            channel_id=cache.channel_id,
            published=cache.published,
            video_id=cache.video_id
        )
