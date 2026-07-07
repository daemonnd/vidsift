from enum import Enum


class DiscoverySource(str, Enum):
    RSS = "rss"
    YT_DLP_FALLBACK = "yt_dlp_fallback"
