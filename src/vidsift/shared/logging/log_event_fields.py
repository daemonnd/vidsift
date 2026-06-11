class LogEvent:
    # orchestrator events
    ORCHESTRATOR_STARTED = "orchestrator_started"
    ORCHESTRATOR_STOPPED = "orchestrator_stopped"

    # interrupted processed events
    INTERRUPTED_PROCESSING_STARTED = "interrupted_processing_started"

    VALIDATION_RESUME_STARTED = "validation_resume_started"
    DOWNLOAD_RESUME_STARTED = "download_resume_started"
    SUMMARIZATION_RESUME_STARTED = "summarization_resume_started"

    # new video events
    VIDEO_SKIPPED_EXISTING = "video_skipped_existing"

    VIDEO_PROCESSING_STARTED = "video_processing_started"
    VIDEO_PROCESSING_COMPLETED = "video_processing_completed"
    VIDEO_PROCESSING_FAILED = "video_processing_failed"

    # rss fetching events
    RSS_FETCH_STARTED = "rss_fetch_started"
    RSS_FETCH_FAILED = "rss_fetch_failed"
    RSS_FETCH_COMPLETED = "rss_fetch_completed"

    # video validation events
    VIDEO_VALIDATED = "video_validated"
    VIDEO_VALIDATION_FAILED = "video_validation_failed"

    # transcript fetching events
    TRANSCRIPT_FETCH_STARTED = "transcript_fetch_started"
    TRANSCRIPT_FETCH_FAILED = "transcript_fetch_failed"
    TRANSCRIPT_FETCH_COMPLETED = "transcript_fetch_completed"
    TRANSCRIPT_PROVIDER_STARTED = "transcript_provider_attempt"
    TRANSCRIPT_PROVIDER_FAILED = "transcript_provider_failed"
    TRANSCRIPT_PROVIDER_COMPLETED = "transcript_provider_completed"

    # video download events
    VIDEO_DOWNLOAD_STARTED = "video_download_started"
    VIDEO_DOWNLOAD_COMPLETED = "video_download_completed"
    VIDEO_DOWNLOAD_FAILED = "video_download_failed"

    # video summarization events
    VIDEO_SUMMARIZATION_STARTED = "video_summarization_started"
    VIDEO_SUMMARIZATION_COMPLETED = "video_summarization_completed"
    VIDEO_SUMMARIZATION_FAILED = "video_summarization_failed"
