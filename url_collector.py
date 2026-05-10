
import feedparser

from errorprotocol import logger
from video_data import Video

log = logger()

YOUTUBE_RSS_URL_BASE: str = "https://www.youtube.com/feeds/videos.xml?channel_id="


channel_id="UC9x0AN7BWHpCDHSm9NiJFJQ"
channel_feed=f"{YOUTUBE_RSS_URL_BASE}{channel_id}"


d = feedparser.parse(channel_feed)

videos: list[Video] = []
channel_id_dict: dict = {}
for entry in d.entries:
    # collects:
    # title
    # author
    # link
    # published

    if entry.title == entry.author:
        continue
    if "/shorts/" in entry.link:
        continue

    channel_id_dict[channel_id] = {
        "link": {}
    }
    video = Video(
        title=str(entry.title), author=str(entry.author),
        link=str(entry.link),
        published=str(entry.published)
    )
    videos.append(video)

for v in videos:
    log.log_info(str(v))


