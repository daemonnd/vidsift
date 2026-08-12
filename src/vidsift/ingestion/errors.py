class VideoDataCollectionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidHTTPStatusError(VideoDataCollectionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ConnectionError(VideoDataCollectionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ReadingError(VideoDataCollectionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NonWellFormattedFeedError(VideoDataCollectionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# for metadata collection
class MetadataCollectionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# for video filtering
class VideoFilteringError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class IngestionEnrichmentError(Exception): # for enrichment of video data after ingestion with yt-dlp
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
