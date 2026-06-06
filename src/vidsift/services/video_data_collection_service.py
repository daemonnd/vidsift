from typing import Generator

from feedparser import FeedParserDict

from vidsift.ingestion.errors import (InvalidHTTPStatusError,
                                      NonWellFormattedFeedError,
                                      VideoDataCollectionError)
from vidsift.ingestion.url_collector import UrlCollector
from vidsift.models.video import Video
from vidsift.shared.errorprotocol import logger

log = logger()


class VideoDataCollection:
    def __init__(self, channel_id_list: list[str]) -> None:
        self.channel_id_list: list[str] = channel_id_list
        if not self.channel_id_list:
            raise VideoDataCollectionError("The given channel id list is empty, no data can be collected")

    @log.log
    def get_videos_to_process(self, ) -> Generator[Video, None, None]:
        data_collector: UrlCollector = UrlCollector(channel_id_list=self.channel_id_list)

        for channel in self.channel_id_list:
            try:
                feed: FeedParserDict = data_collector.fetch_feed(channel_id=channel)
                data_collector.validate_feed_response(feed, channel)
                current_channel_data = data_collector.parse_one_channel(feed=feed, channel_id=channel)
                for video in current_channel_data:
                    yield video

            except InvalidHTTPStatusError as e:
                log.log_warning(f"InvalidHTTPStatusError: The HTTP Status of the feed seems to be corrupt: {str(e)}")
                log.log_warning(f"Failed to fetch the data of channel {channel}")
                continue
            except NonWellFormattedFeedError as e:
                log.log_warning(f"NonWellFormattedFeedError: {str(e)}")
                log.log_warning(f"Failed to fetch the data of channel {channel}")
                continue
            except VideoDataCollectionError as e:
                log.log_warning(f"VideoDataCollectionError: {str(e)}")
                log.log_warning(f"Failed to fetch the data of channel {channel}")
                continue
