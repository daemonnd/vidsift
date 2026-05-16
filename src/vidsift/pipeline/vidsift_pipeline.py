"""
Vidsifts orchestrator
It gets called by main.py

The ONLY top-level orchestrator

What it does:
- define pipeline stages
- control ordering
- pass structured data between steps
- handle reties/failure strategy
"""



# feature/transcript
from ..features.transcript.errors import (TranscriptDownloadError,
                                          TranscriptError,
                                          TranscriptFetchingBlockedError,
                                          TranscriptFetchingError,
                                          TranscriptNotAvailibleError,
                                          TranscriptNotFoundError,
                                          VTTFileReadingError)
from ..features.transcript.fetcher import TranscriptFetcher
from ..features.transcript.vtt_transcript_extractor import \
    VTTranscriptExtractor
# data
from ..models.video import Video
# utils
from ..shared.errorprotocol import logger

log: logger = logger()

class VidsiftOrchestrator:
    def __init__(self) -> None:
        # transcript
        self.transcript_fetcher: TranscriptFetcher = TranscriptFetcher()
        self.vtt_transcript_extractor: VTTranscriptExtractor = VTTranscriptExtractor()


    def fetch_and_download_transcript(self, video: Video) -> str | None:
        transcript: str | None = None
        log.log_debug("Trying to fetch and download the transcript with yt-dlp...")
        transcript = self.fetch_and_download_transcript_yt_dlp(video)
        if transcript is None:
            log.log_warning("Fetching and downloading the transcript with yt-dlp failed")
            transcript = self.fetch_and_download_transcript_transcript_api(video)
            if transcript is None:
                log.log_error(f"Failed to fetch the transcript of video {video.title} with url {video.url}")
        return transcript

    def fetch_and_download_transcript_yt_dlp(self, video: Video) -> str | None:
        # fetch the transcript and save it to a file
        yt_dlp_error_start: str = "Error while fetching and downloading the transcript with yt-dlp:"
        try:
            self.transcript_fetcher.extract_transcript_yt_dlp(video_url=video.url)
        except TranscriptDownloadError as e:
            log.log_error(f"TranscriptDownloadError: {yt_dlp_error_start} {e}")
        except TranscriptFetchingBlockedError as e:
            log.log_error(f"TranscriptFetchingBlockedError: {yt_dlp_error_start} {e}")
        except TranscriptFetchingError as e:
            log.log_error(f"TranscriptFetchingError: {yt_dlp_error_start} {e}")
        except TranscriptNotAvailibleError as e:
            log.log_error(f"TranscriptNotAvailibleError: {yt_dlp_error_start} {e}")
        except TranscriptError as e:
            log.log_error(f"TranscriptError: {yt_dlp_error_start} {e}")
        except Exception as e:
            log.log_error(f"Exception: {yt_dlp_error_start} {e}")
        else:
            try:
                # get the transcript out of the vtt file
                return self.vtt_transcript_extractor.convert_vtt_to_str(self.vtt_transcript_extractor.find_vtt_file(video.video_id))
            except TranscriptNotFoundError as e:
                log.log_error(f"TranscriptNotFoundError: {yt_dlp_error_start} {e}")
            except VTTFileReadingError as e:
                log.log_error(f"VTTFileReadingError: {yt_dlp_error_start} {e}")
            except TranscriptError as e:
                log.log_error(f"TranscriptError: {yt_dlp_error_start} {e}")
            except Exception as e:
                log.log_error(f"Exception: {yt_dlp_error_start} {e}")

    def fetch_and_download_transcript_transcript_api(self, video: Video) -> str | None:
        youtube_transcript_api_error_start: str = "Error while fetching and downloading the transcript with youtube transcript api:"
        try:
            log.log_debug("Trying to get the transcript with youtube_transcript_api...")
            return self.transcript_fetcher.extract_transcript(video_id=video.video_id)
        except TranscriptDownloadError as e:
            log.log_error(f"TranscriptDownloadError: {youtube_transcript_api_error_start} {e}")
        except TranscriptFetchingBlockedError as e:
            log.log_error(f"TranscriptFetchingBlockedError: {youtube_transcript_api_error_start} {e}")
        except TranscriptFetchingError as e:
            log.log_error(f"TranscriptFetchingError: {youtube_transcript_api_error_start} {e}")
        except TranscriptNotAvailibleError as e:
            log.log_error(f"TranscriptNotAvailibleError: {youtube_transcript_api_error_start} {e}")
        except TranscriptError as e:
            log.log_error(f"TranscriptError: {youtube_transcript_api_error_start} {e}")
        except Exception as e:
            log.log_error(f"Exception: {youtube_transcript_api_error_start} {e}")


if __name__ == "__main__":
    vo = VidsiftOrchestrator()
    video_object = Video(
        title="Your Remote Desktop SUCKS!! Try this instead (FREE + Open Source)",
        url="https://www.youtube.com/watch?v=EXL8mMUXs88",
        author="NetworkChuck",
        published="somedate",
        video_id="EXL8mMUXs88"
    )
    print(vo.fetch_and_download_transcript(video_object))
