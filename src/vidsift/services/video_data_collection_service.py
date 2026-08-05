import logging
from typing import Generator

from feedparser import FeedParserDict

from vidsift.config.models import AppConfig
from vidsift.ingestion.errors import VideoDataCollectionError
from vidsift.ingestion.rss_url_collector import RSSUrlCollector
from vidsift.ingestion.yt_dlp_url_collector import YtDlpUrlCollector
from vidsift.models.video import Video
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.video_discovery_source import DiscoverySource

logger = logging.getLogger(__name__)


class VideoDataCollection:
    def __init__(self, channel_id_list: list[str], config: AppConfig) -> None:
        self.config: AppConfig = config
        self.channel_id_list: list[str] = channel_id_list

        if not self.channel_id_list:
            raise VideoDataCollectionError(
                "The given channel id list is empty, no data can be collected"
            )

    def get_videos_to_process(
        self,
    ) -> Generator[tuple[Video, DiscoverySource], None, None]:
        rss_collector: RSSUrlCollector = RSSUrlCollector(
            channel_id_list=self.channel_id_list, config=self.config
        )
        yt_dlp_collector: YtDlpUrlCollector = YtDlpUrlCollector(config=self.config)

        logger.info(
            "Starting RSS feed collection.",
            extra={
                "event": LogEvent.RSS_FETCH_STARTED,
                "channel_count": len(self.channel_id_list),
            },
        )

        try:
            for channel in self.channel_id_list:
                logger.debug(
                    f"Fetching RSS feed for channel: {channel}",
                    extra={
                        "event": LogEvent.RSS_CHANNEL_FETCH_STARTED,
                        "channel_id": channel,
                    },
                )
                try:
                    feed: FeedParserDict = rss_collector.fetch_feed(channel_id=channel)

                    rss_collector.validate_feed_response(
                        feed,
                        channel,
                    )

                    current_channel_data = rss_collector.parse_one_channel(
                        feed=feed,
                        channel_id=channel,
                    )

                    for video in current_channel_data:
                        yield video, DiscoverySource.RSS

                except VideoDataCollectionError as e:
                    logger.warning(
                        f"Failed to collect video data from RSS feed: {str(e)}",
                        extra={
                            "event": LogEvent.RSS_CHANNEL_FETCH_FAILED,
                            "channel_id": channel,
                        },
                        exc_info=True,
                    )

                    # fall back to yt-dlp url collector

                    logger.debug(
                        "Starting yt-dlp data collection as fallback for failing rss...",
                        extra={
                            "event": LogEvent.YT_DLP_CHANNEL_FETCH_STARTED,
                            "channel_id": channel,
                        },
                    )
                    try:
                        current_channel_data = yt_dlp_collector.parse_one_channel(
                            channel_id=channel
                        )
                        for video in current_channel_data:
                            yield video, DiscoverySource.YT_DLP_FALLBACK

                    except VideoDataCollectionError as e:
                        logger.warning(
                            f"Failed to collect video data for channel id {channel}: {str(e)}",
                            exc_info=True,
                            extra={
                                "event": LogEvent.YT_DLP_CHANNEL_FETCH_FAILED,
                                "channel_id": channel,
                            },
                        )

        except BaseException:
            raise
        else:
            logger.info(
                "RSS feed collection completed successfully.",
                extra={
                    "event": LogEvent.RSS_FETCH_COMPLETED,
                },
            )
