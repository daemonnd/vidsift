from typing import Literal


class LogEvent:
    @staticmethod
    def get_final_output_events(general_event: Literal["download", "summarize"]):
        """
        Get the events in a tuple of started, completed and failed from a general event
        """
        match general_event:
            case "download":
                return (
                    LogEvent.VIDEO_DOWNLOAD_STARTED,
                    LogEvent.VIDEO_DOWNLOAD_COMPLETED,
                    LogEvent.VIDEO_DOWNLOAD_FAILED,
                )
            case "summarize":
                return (
                    LogEvent.VIDEO_SUMMARIZATION_STARTED,
                    LogEvent.VIDEO_SUMMARIZATION_COMPLETED,
                    LogEvent.VIDEO_SUMMARIZATION_FAILED,
                )

    # run events
    RUN_STARTED = "run_started"
    CONFIG_LOADED = "config_loaded"
    RUN_COMPLETED = "run_completed"
    # orchestrator events
    ORCHESTRATOR_STARTED = "orchestrator_started"
    ORCHESTRATOR_STOPPED = "orchestrator_stopped"
    ORCHESTRATOR_INTERRUPTED = "orchestrator_interrupted"

    # single video manual runs
    MANUAL_DOWNLOAD_RUN_STARTED = "manual_download_run_started"
    MANUAL_FAKE_DOWNLOAD_RUN_STARTED = "manual_fake_download_run_started"
    MANUAL_SUMMARIZATION_RUN_STARTED = "manual_summarization_run_started"

    # invalid video event
    INVALID_VIDEO = "invalid_video"

    # interrupted processed events
    INTERRUPTED_PROCESSING_STARTED = "interrupted_processing_started"
    INTERRUPTED_PROCESSING_COMPLETED = "interrupted_processing_completed"

    VIDEO_METADATA_ENRICHMENT_RESUME_STARTED = "video_metadata_enrichment_resume_started"
    PROCESSING_VIDEO_METADATA_ENRICHMENT_RESUME = "processing_video_metadata_enrichment_resume"
    VIDEO_METADATA_ENRICHMENT_RESUME_COMPLETED = "video_metadata_enrichment_resume_completed"
    VIDEO_METADATA_ENRICHMENT_RESUME_FAILED = "video_metadata_enrichment_resume_failed"

    VALIDATION_RESUME_STARTED = "validation_resume_started"
    PROCESSING_VALIDATION_RESUME = "processing_validation_resume"
    VALIDATION_RESUME_COMPLETED = "validation_resume_completed"

    DOWNLOAD_RESUME_STARTED = "download_resume_started"
    PROCESSING_DOWNLOAD_RESUME = "processing_download_resume"
    DOWNLOAD_RESUME_COMPLETED = "download_resume_completed"

    SUMMARIZATION_RESUME_STARTED = "summarization_resume_started"
    PROCESSING_SUMMARIZATION_RESUME = "processing_summarization_resume"
    SUMMARIZATION_RESUME_COMPLETED = "summarization_resume_completed"

    # video delay events
    VIDEO_DELAY_STARTED = "video_delay_started"
    VIDEO_DELAY_COMPLETED = "video_delay_completed"

    # new video events
    VIDEO_SKIPPED_EXISTING = "video_skipped_existing"

    VIDEO_PROCESSING_STARTED = "video_processing_started"
    VIDEO_PROCESSING_COMPLETED = "video_processing_completed"
    VIDEO_PROCESSING_FAILED = "video_processing_failed"

    NO_VIDEO_GETS_PROCESSED = "no_video_gets_processed"

    # rss fetching events
    RSS_FETCH_STARTED = "rss_fetch_started"
    RSS_FETCH_FAILED = "rss_fetch_failed"
    RSS_FETCH_COMPLETED = "rss_fetch_completed"

    RSS_CHANNEL_FETCH_STARTED = "rss_channel_fetch_started"
    RSS_CHANNEL_FETCH_FAILED = "rss_channel_fetch_failed"

    # yt-dlp fetching events
    YT_DLP_CHANNEL_FETCH_STARTED = "yt_dlp_fetch_started"
    YT_DLP_CHANNEL_FETCH_FAILED = "yt_dlp_fetch_failed"
    YT_DLP_CHANNEL_FETCH_COMPLETED = "yt_dlp_fetch_completed"

    # video metadata enrichment events
    VIDEO_METADATA_ENRICHMENT_STARTED = "video_metadata_enrichment_started"
    VIDEO_METADATA_ENRICHMENT_COMPLETED = "video_metadata_enrichment_completed"
    VIDEO_METADATA_ENRICHMENT_FAILED = "video_metadata_enrichment_failed"

    # video filtering events
    VIDEO_FILTERING_STARTED = "video_filtering_started"
    VIDEO_FILTERING_COMPLETED = "video_filtering_completed"
    VIDEO_FILTERING_FAILED = "video_filtering_failed"

    # pre-validation events
    PRE_VALIDATION_STARTED = "pre_validation_started"
    PRE_VALIDATION_COMPLETED = "pre_validation_completed"
    PRE_VALIDATION_FAILED = "pre_validation_failed"

    # video validation events
    PRE_VALIDATION_EMOJI_RATIO_CALCULATED = "pre_validation_emoji_ratio_calculated"
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
    VIDEO_SUMMARIZATION_SKIPPED = "video_summarization_skipped"

    # scheduler events
    SCHEDULER_STARTED = "scheduler_started"
    SCHEDULER_FAILED = "scheduler_failed"
    SCHEDULER_COOLDOWN_STARTED = "scheduler_cooldown_started"
    SCHEDULER_COOLDOWN_COMPLETED = "scheduler_cooldown_completed"

    # locking events
    LOCK_ACQUIRED = "lock_acquired"
    LOCK_RELEASED = "lock_released"
    LOCK_FAILED = "lock_failed"

    # video display events
    VIDEO_PROCESSING_ERROR = "video_processing_error"
