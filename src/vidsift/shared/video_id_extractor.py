import logging

logger = logging.getLogger(__name__)
class VideoIDExtractor:
    def __init__(self) -> None:
        pass

    def extract_id(self, url: str) -> str:
        try:
            url_parts: list[str] = url.split("v=")
            return url_parts[1].split("&")[0]
        except Exception as e:
            logger.exception(f"Failed to extract the video id of url '{url}', make sure it is an actual youtube video url: {str(e)}")
            raise

if __name__ == "__main__":
    vie = VideoIDExtractor()
    print(vie.extract_id("https://www.youtube.com/watch?v=0Tch0N5nsRU"))
    print(vie.extract_id("https://www.youtube.com/watch?v=k02P5nghmfs&list=PLIhvC56v63ILr2oFbK-Yj9jnIdqSLwCFU"))
