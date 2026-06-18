from typing import Generator

import feedparser
from feedparser import FeedParserDict

from vidsift.ingestion.errors import (InvalidHTTPStatusError,
                                      NonWellFormattedFeedError)
from vidsift.models.video import InvalidVideoError, Video
from vidsift.shared.video_id_extractor import VideoIDExtractor

YOUTUBE_BASE_RSS_URL: str = "https://www.youtube.com/feeds/videos.xml?channel_id="
id_extractor = VideoIDExtractor()

class UrlCollector:
    def __init__(self, channel_id_list: list[str]) -> None:
        self.channel_id_list: list = channel_id_list

        if self.channel_id_list == []:
            raise  ValueError("The channel ID list given for fetching video data is empty")



    def fetch_feed(self, channel_id: str) -> FeedParserDict:
        return feedparser.parse(f"{YOUTUBE_BASE_RSS_URL}{channel_id}")

    def validate_feed_response(self, feed: FeedParserDict, channel_id: str) -> None:
        """
        Method to validate if the feed is okay, if not it raises
        Raises:
        - InvalidHTTPStatusError if HTTP status is not 200
        - NonWellFormattedFeedError if feed is unwell parsed
        """
        if feed.status != 200:
            raise InvalidHTTPStatusError(f"The HTTP status of {YOUTUBE_BASE_RSS_URL}{channel_id} is {feed.status}, which is not 200")
        if feed.bozo == 1:
            raise NonWellFormattedFeedError(f"Bozo of {YOUTUBE_BASE_RSS_URL}{channel_id} is 1, indicating that the feed is non-well-formed")


    def parse_one_channel(self,  feed: FeedParserDict, channel_id: str) -> Generator[Video, None, None]:
        """
        Method to get a list of Video objects of one channel
        Raises:
        - InvalidHTTPStatusError if the status is not 200
        """

        #channel_id_dict: dict = {}

        for entry in feed.entries:
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

            #channel_id_dict[channel_id] = {
            #"link": {}
            #}
            try:
                video = Video(
                    title=str(entry.title), author=str(entry.author),
                    url=str(entry.link),
                    published=str(entry.published),
                    video_id=id_extractor.extract_id(str(entry.link)),
                    channel_id=channel_id
                )
            except InvalidVideoError:
                raise
            yield video



if __name__ == "__main__":
    channel_id_list: list = ["UC9x0AN7BWHpCDHSm9NiJFJQ","UCo71RUe6DX4w-Vd47rFLXPg"]
    url_collectr: UrlCollector = UrlCollector(channel_id_list=channel_id_list)
    to_process = url_collectr.parse_all_channels()
    for i in to_process:
        print(i)
