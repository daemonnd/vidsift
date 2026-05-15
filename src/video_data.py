from dataclasses import dataclass


@dataclass
class Video:
    title: str
    url: str
    author: str
    published: str
    video_id: str
    #channel_id: str
