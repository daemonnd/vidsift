import logging
from datetime import datetime, timedelta
from typing import Generator

import certifi
import feedparser
import httpx
from feedparser import FeedParserDict
from httpx import (ConnectError, DecodingError, HTTPStatusError, ReadError,
                   RequestError)

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import (ConnectionError, InvalidHTTPStatusError,
                                      NonWellFormattedFeedError, ReadingError)
from vidsift.models.video import InvalidVideoError, Video
from vidsift.shared.video_id_extractor import VideoIDExtractor

logger = logging.getLogger(__name__)

YOUTUBE_BASE_RSS_URL: str = "https://www.youtube.com/feeds/videos.xml?channel_id="
id_extractor = VideoIDExtractor()

class RSSUrlCollector:
    def __init__(self, channel_id_list: list[str], config: AppConfig) -> None:
        self.config: AppConfig = config

        self.channel_id_list: list = channel_id_list
        if self.channel_id_list == []:
            raise  ValueError("The channel ID list given for fetching video data is empty")



    def fetch_feed(self, channel_id: str) -> FeedParserDict:
        """
        Fetches the feed for a given channel ID and returns the parsed feed.
        Raises:
            - InvalidHTTPStatusError if the HTTP request fails or returns a non-200 status code.
            - ConnectionError if the connection failed
            - ReadingError is reading the response failed
        Returns:
            - the parsed xml feed as a FeedParserDict.
        """
        url = f"{YOUTUBE_BASE_RSS_URL}{channel_id}"

        try:
            with httpx.Client(verify=certifi.where(), timeout=10.0) as client:
                response = client.get(url)
                try:
                    response.raise_for_status()
                except HTTPStatusError as e:
                    raise InvalidHTTPStatusError(f"HTTP request failed for {url}: {e.response.status_code} {e.response.reason_phrase}")

            return feedparser.parse(response.content)
        except ConnectError as e:
            raise ConnectionError(f"Failed to connect to {url}: {e}") from e 
        except ReadError as e:
            raise ReadingError(f"Failed to read from {url}: {e}") from e
        except DecodingError as e:
            raise ReadingError(f"Failed to decode {url}: {e}") from e
        except RequestError as e:
            raise ConnectionError(f"Failed to do a request to {url}: {e}") from e

    def validate_feed_response(self, feed: FeedParserDict, channel_id: str) -> None:
        """
        Method to validate if the feed is okay, if not it raises
        Raises:
        - NonWellFormattedFeedError if feed is unwell parsed
        """
        bozo = feed.get('bozo')
        if bozo == 1:
            match self.config.video_fetching.rss_bozo_level:
                case "ignore":
                    pass
                case "debug":
                    logger.warning(f"Bozo of {YOUTUBE_BASE_RSS_URL}{channel_id} is 1: {feed.get('bozo_exception')}")
                case "permissive":
                    logger.warning(f"Bozo of {YOUTUBE_BASE_RSS_URL}{channel_id} is 1")
                case "strict":
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

            try:
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
            except Exception as e:
                logger.warning(f"Failed to parse video entry for channel {channel_id}: {e}")
            else:
                yield video
