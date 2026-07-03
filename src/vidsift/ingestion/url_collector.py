import ssl
import urllib.request
from datetime import datetime, timedelta
from typing import Generator

import certifi
import feedparser
from feedparser import FeedParserDict

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import (InvalidHTTPStatusError,
                                      NonWellFormattedFeedError)
from vidsift.models.video import InvalidVideoError, Video
from vidsift.shared.video_id_extractor import VideoIDExtractor

YOUTUBE_BASE_RSS_URL: str = "https://www.youtube.com/feeds/videos.xml?channel_id="
id_extractor = VideoIDExtractor()

class UrlCollector:
    def __init__(self, channel_id_list: list[str], config: AppConfig) -> None:
        self.config: AppConfig = config

        self.channel_id_list: list = channel_id_list
        if self.channel_id_list == []:
            raise  ValueError("The channel ID list given for fetching video data is empty")



    def fetch_feed(self, channel_id: str) -> FeedParserDict:
        context = ssl.create_default_context(cafile=certifi.where())
        response = urllib.request.urlopen(f"{YOUTUBE_BASE_RSS_URL}{channel_id}", context=context)
        raw_xml = response.read()
        return feedparser.parse(raw_xml)

    def validate_feed_response(self, feed: FeedParserDict, channel_id: str) -> None:
        """
        Method to validate if the feed is okay, if not it raises
        Raises:
        - InvalidHTTPStatusError if HTTP status is not 200
        - NonWellFormattedFeedError if feed is unwell parsed
        """
        status = feed.get('status')
        if status != 200:
            raise InvalidHTTPStatusError(f"The HTTP status of {YOUTUBE_BASE_RSS_URL}{channel_id} is {status}, which is not 200")
        bozo = feed.get('bozo')
        if bozo == 1:
            raise NonWellFormattedFeedError(f"Bozo of {YOUTUBE_BASE_RSS_URL}{channel_id} is 1: {feed.get("bozo_exception")}")


    def parse_one_channel(self,  feed: FeedParserDict, channel_id: str) -> Generator[Video, None, None]:
        """
        Method to get a list of Video objects of one channel
        Raises:
        - InvalidHTTPStatusError if the status is not 200
        """

        #channel_id_dict: dict = {}

        for entry in feed.get("entries", []):
            # collects:
            # title
            # author
            # link
            # published

            # not add channel creation and shorts to the list
            if entry.get('title') == entry.get('author'):
                continue
            if "/shorts/" in entry.link:
                continue
            # skip videos that are less recent than specified in the config
            video_upload_time = datetime.fromisoformat(str(entry.published))
            oldest_allowed_date = datetime.now() - timedelta(days=self.config.video_processing.days_uploaded_before)
            if video_upload_time.timestamp() < oldest_allowed_date.timestamp():
                continue

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
