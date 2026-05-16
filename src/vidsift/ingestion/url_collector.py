import feedparser

from vidsift.models.video import Video
from vidsift.shared.errorprotocol import logger
from vidsift.shared.video_id_extractor import VideoIDExtractor

log = logger()

YOUTUBE_BASE_RSS_URL: str = "https://www.youtube.com/feeds/videos.xml?channel_id="
id_extractor = VideoIDExtractor()

class UrlCollector:
    def __init__(self, channel_id_list: list[Video]) -> None:
        self.channel_id_list: list = channel_id_list

    def parse_all_channels(self) -> list[Video]:
        """
        Method to iterate over the channel id list and put all the results in a list that gets returned
        """
        self.video_list: list[Video] = []
        for channel in self.channel_id_list:
            self.video_list.extend(self.parse_one_channel(channel))

        return self.video_list


    def parse_one_channel(self,  channel_id: str) -> list[Video]:
        """
        Method to get a list of Video objects of one channel
        """
        result = feedparser.parse(f"{YOUTUBE_BASE_RSS_URL}{channel_id}")

        videos: list[Video] = []
        channel_id_dict: dict = {}

        try:
            for entry in result.entries:
                # collects:
                # title
                # author
                # link
                # published

                # not add channel creation and shorts to the list
                if entry.title == entry.author:
                    continue
                if "/shorts/" in entry.link:
                    continue

                channel_id_dict[channel_id] = {
                    "link": {}
                }
                video = Video(
                    title=str(entry.title), author=str(entry.author),
                    url=str(entry.link),
                    published=str(entry.published),
                    video_id=id_extractor.extract_id(str(entry.link))
                )
                videos.append(video)
        except KeyError as e:
            log.log_error(f"KeyError while parsing one channel: One entry seems to be nonexistant: {e}")
        except Exception as e:
            log.log_error(f"Exception while parsing one channel: {e}")

        return videos



if __name__ == "__main__":
    channel_id_list: list = ["UC9x0AN7BWHpCDHSm9NiJFJQ","UCo71RUe6DX4w-Vd47rFLXPg"]
    url_collectr: UrlCollector = UrlCollector(channel_id_list=channel_id_list)
    to_process = url_collectr.parse_all_channels()
    for i in to_process:
        print(i)
