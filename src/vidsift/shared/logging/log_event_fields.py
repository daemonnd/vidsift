from typing import Literal


class LogEvent:
    @staticmethod
    def get_final_output_events(general_event: Literal["download", "summarize"]):
        """
        Get the events in a tuple of started, completed and failed from a general event
        """
        match general_event:
            case "download":
                return LogEvent.VIDEO_DOWNLOAD_STARTED, LogEvent.VIDEO_DOWNLOAD_COMPLETED, LogEvent.VIDEO_DOWNLOAD_FAILED
            case "summarize":
                return LogEvent.VIDEO_SUMMARIZATION_STARTED, LogEvent.VIDEO_SUMMARIZATION_COMPLETED, LogEvent.VIDEO_SUMMARIZATION_FAILED
    # orchestrator events
    ORCHESTRATOR_STARTED = "orchestrator_started"
    ORCHESTRATOR_STOPPED = "orchestrator_stopped"
    ORCHESTRATOR_INTERRUPTED = "orchestrator_interrupted"

    # invalid video event
    INVALID_VIDEO = "invalid_video"

    # interrupted processed events
    INTERRUPTED_PROCESSING_STARTED = "interrupted_processing_started"
    INTERRUPTED_PROCESSING_COMPLETED = "interrupted_processing_completed"

    VALIDATION_RESUME_STARTED = "validation_resume_started"
    DOWNLOAD_RESUME_STARTED = "download_resume_started"
    SUMMARIZATION_RESUME_STARTED = "summarization_resume_started"

    # video delay events
    VIDEO_DELAY_STARTED = "video_delay_started"
    VIDEO_DELAY_COMPLETED = "video_delay_completed"

    # new video events
    VIDEO_SKIPPED_EXISTING = "video_skipped_existing"

    VIDEO_PROCESSING_STARTED = "video_processing_started"
    VIDEO_PROCESSING_COMPLETED = "video_processing_completed"
    VIDEO_PROCESSING_FAILED = "video_processing_failed"

    # rss fetching events
    RSS_FETCH_STARTED = "rss_fetch_started"
    RSS_FETCH_FAILED = "rss_fetch_failed"
    RSS_FETCH_COMPLETED = "rss_fetch_completed"

    # pre-validation events
    PRE_VALIDATION_STARTED = "pre_validation_started"
    PRE_VALIDATION_COMPLETED = "pre_validation_completed"
    PRE_VALIDATION_FAILED = "pre_validation_failed"

    # video validation events
    VIDEO_VALIDATION_STARTED = "video_validation_started"
    VIDEO_VALIDATION_FAILED = "video_validation_failed"
    VIDEO_VALIDATION_COMPLETED = "video_validation_completed"

    # metadate fetching events
    METADATA_FETCH_STARTED = "metadata_fetch_strarted"
    METADATA_FETCH_COMPLETED = "metadata_fetch_completed"
    METADATA_FETCH_FAILED = "metadata_fetch_failed"

    # transcript fetching events
    TRANSCRIPT_FETCH_STARTED = "transcript_fetch_started"
    TRANSCRIPT_FETCH_FAILED = "transcript_fetch_failed"
    TRANSCRIPT_FETCH_COMPLETED = "transcript_fetch_completed"
    TRANSCRIPT_PROVIDER_STARTED = "transcript_provider_attempt"
    TRANSCRIPT_PROVIDER_FAILED = "transcript_provider_failed"
    TRANSCRIPT_PROVIDER_COMPLETED = "transcript_provider_completed"

    # transcript summarization events
    TRANSCRIPT_SUMMARIZATION_STARTED = "transcript_summarization_started"
    TRANSCRIPT_SUMMARIZATION_COMPLETED = "transcript_summarization_completed"
    TRANSCRIPT_SUMMARIZATION_FAILED = "transcript_summarization_failed"
    CHUNK_SUMMARIZATION_STARTED = "chunk_summarization_started"
    CHUNK_SUMMARIZATION_COMPLETED = "chunk_summarization_completed"
    CHUNK_SUMMARIZATION_FAILED = "chunk_summarization_failed"

    # AI JSON output events
    AI_JSON_OUTPUT_STARTED = "ai_json_output_started"
    AI_JSON_OUTPUT_COMPLETED = "ai_json_output_completed"
    AI_JSON_OUTPUT_FAILED = "ai_json_output_failed"
    AI_RESPONSE_VALIDATION_STARTED = "ai_response_validation_started"
    AI_RESPONSE_VALIDATION_COMPLETED = "ai_response_validation_completed"
    AI_RESPONSE_VALIDATION_FAILED = "ai_response_validation_failed"

    # video download events
    VIDEO_DOWNLOAD_STARTED = "video_download_started"
    VIDEO_DOWNLOAD_COMPLETED = "video_download_completed"
    VIDEO_DOWNLOAD_FAILED = "video_download_failed"

    # video summarization events
    VIDEO_SUMMARIZATION_STARTED = "video_summarization_started"
    VIDEO_SUMMARIZATION_COMPLETED = "video_summarization_completed"
    VIDEO_SUMMARIZATION_FAILED = "video_summarization_failed"
