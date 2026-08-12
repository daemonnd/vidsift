import logging
from pathlib import Path

from vidsift.config.models import AppConfig
from vidsift.features.download.downloader import VideoDownloader
from vidsift.ingestion.metadata_collector import MetadataCollector
from vidsift.models.video import InvalidVideoError, Video
from vidsift.models.video_record import VideoProcessingStatus
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.runtime.lock_manager import LockManager
from vidsift.services.summarization_service import SummarizationService
from vidsift.services.validation_service import VideoValidator
from vidsift.shared.execution_context import (RunContext, reset_run_context,
                                              set_run_context)
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.run_manager import RunManager


def register_process(subparsers):
    process_parser = subparsers.add_parser(
        "process",
        help="Process a certain URL ",
        usage="--url is required. \nIf only --url is selected, the video will be validated + discarded / summarized / downloaded"
        )
    exclusive_process_parser_group = process_parser.add_mutually_exclusive_group()
    process_parser.add_argument(
        "--url",
        help="Process a specific video",
        required=True
    )
    exclusive_process_parser_group.add_argument(
        "--download",
        help="Download the selected video",
        action="store_true",
    )
    exclusive_process_parser_group.add_argument(
        "--summarize",
        help="Summarize the selected video",
        action="store_true"
    )
    exclusive_process_parser_group.add_argument(
        "--fetch-transcript",
        help="Fetch the transcript of the selected video",
        action="store_true"
    )
    process_parser.set_defaults(
        func=handle_process
    )
    return process_parser


def handle_process(args, config: AppConfig, run_id):
    run_manager: RunManager = RunManager(run_id)
    run_manager.start_run(run_type="manual_pipeline_run")
    try:
        orchestrator = VidsiftOrchestrator(
            config=config
        )
        logger = logging.getLogger(__name__)
        if args.download:
            from vidsift.shared.video_id_extractor import VideoIDExtractor
            logger.info(
                f"Starting manual download with url {args.url}",
                extra={
                    "event": LogEvent.MANUAL_DOWNLOAD_RUN_STARTED,
                    "video_id": VideoIDExtractor().extract_id(args.url)
                }
            )
            downloader: VideoDownloader = VideoDownloader(config=config)
            downloader.download(
                video_url=args.url,
                output_path=Path(config.downloads.output_dir)
            )
            return

        metadata_collector = MetadataCollector(config=config)
        try:
            vid: Video = metadata_collector.fetch_metadata(args.url)
        except InvalidVideoError:
            raise
        else:
            transcript = orchestrator.fetch_transcript(
                vid=vid
            )
            if args.summarize:
                logger.info(
                    f"Starting manual summarization with video id '{vid.video_id}'",
                    extra={
                        "event": LogEvent.MANUAL_SUMMARIZATION_RUN_STARTED,
                        "video_id": vid.video_id
                    }
                )
                summarizer: SummarizationService = SummarizationService(config=config)
                summarizer.summarize(
                    raw_transcript=transcript,
                    vid=vid
                )
            elif args.fetch_transcript:
                print(transcript)
            else:
                video_validator: VideoValidator = VideoValidator(config=config)
                validation_result = video_validator.validate_video(
                    vid=vid,
                    raw_transcript=transcript
                )
                orchestrator.take_action_on_video(
                    vid=vid,
                    video_validation_result=validation_result,
                    transcript=transcript
                )
    finally:
        run_manager.end_run()
