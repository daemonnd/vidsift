import logging
from typing import Generator

from feedparser import FeedParserDict

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import (InvalidHTTPStatusError,
                                      NonWellFormattedFeedError,
                                      VideoDataCollectionError)
from vidsift.ingestion.url_collector import UrlCollector
from vidsift.models.video import Video
from vidsift.shared.logging.log_event_fields import LogEvent

logger = logging.getLogger(__name__)


class VideoDataCollection:
    def __init__(self, channel_id_list: list[str], config: AppConfig) -> None:
        self.config: AppConfig = config
        self.channel_id_list: list[str] = channel_id_list

        if not self.channel_id_list:
            raise VideoDataCollectionError(
                "The given channel id list is empty, no data can be collected"
            )

    def get_videos_to_process(self) -> Generator[Video, None, None]:
        data_collector: UrlCollector = UrlCollector(
            channel_id_list=self.channel_id_list,
            config=self.config
        )

        logger.info(
            "Starting RSS feed collection.",
            extra={
                "event": LogEvent.RSS_FETCH_STARTED,
                "channel_count": len(self.channel_id_list),
            },
        )

        try:
            for channel in self.channel_id_list:
                try:
                    feed: FeedParserDict = data_collector.fetch_feed(
                        channel_id=channel
                    )

                    data_collector.validate_feed_response(
                        feed,
                        channel,
                    )

                    current_channel_data = data_collector.parse_one_channel(
                        feed=feed,
                        channel_id=channel,
                    )

                    for video in current_channel_data:
                        yield video

                except InvalidHTTPStatusError as e:
                    logger.warning(
                        (
                            f"Failed to fetch RSS feed because of an invalid HTTP status: {str(e)}"
                        ),
                        extra={
                            "event": LogEvent.RSS_FETCH_FAILED,
                            "channel_id": channel,
                        },
                    )
                    continue

                except NonWellFormattedFeedError as e:
                    logger.warning(
                        f"Failed to parse malformed RSS feed: {str(e)}",
                        extra={
                            "event": LogEvent.RSS_FETCH_FAILED,
                            "channel_id": channel,
                        },
                    )
                    continue

                except VideoDataCollectionError as e:
                    logger.warning(
                        f"Failed to collect video data from RSS feed: {str(e)}",
                        extra={
                            "event": LogEvent.RSS_FETCH_FAILED,
                            "channel_id": channel,
                        },
                    )
                    continue

        except BaseException:
            raise
        else:
            logger.info(
                "RSS feed collection completed successfully.",
                extra={
                    "event": LogEvent.RSS_FETCH_COMPLETED,
                },
            )
