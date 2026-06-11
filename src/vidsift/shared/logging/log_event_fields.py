class LogEvent:
    ORCHESTRATOR_STARTED = "orchestrator_started"
    ORCHESTRATOR_STOPPED = "orchestrator_stopped"

    INTERRUPTED_PROCESSING_STARTED = "interrupted_processing_started"

    VALIDATION_RESUME_STARTED = "validation_resume_started"
    DOWNLOAD_RESUME_STARTED = "download_resume_started"
    SUMMARIZATION_RESUME_STARTED = "summarization_resume_started"

    VIDEO_DISCOVERED = "video_discovered"
    VIDEO_SKIPPED_EXISTING = "video_skipped_existing"

    VIDEO_PROCESSING_STARTED = "video_processing_started"
    VIDEO_PROCESSING_COMPLETED = "video_processing_completed"
    VIDEO_PROCESSING_FAILED = "video_processing_failed"

    VIDEO_VALIDATED = "video_validated"
    VIDEO_VALIDATION_FAILED = "video_validation_failed"

    TRANSCRIPT_FETCH_FAILED = "transcript_fetch_failed"

    VIDEO_DOWNLOAD_STARTED = "video_download_started"
    VIDEO_DOWNLOAD_COMPLETED = "video_download_completed"
    VIDEO_DOWNLOAD_FAILED = "video_download_failed"

    VIDEO_SUMMARIZATION_STARTED = "video_summarization_started"
    VIDEO_SUMMARIZATION_COMPLETED = "video_summarization_completed"
    VIDEO_SUMMARIZATION_FAILED = "video_summarization_failed"
