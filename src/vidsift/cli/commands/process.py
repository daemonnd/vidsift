from pathlib import Path

from vidsift.config.models import AppConfig
from vidsift.features.download.downloader import VideoDownloader
from vidsift.ingestion.metadata_collector import MetadataCollector
from vidsift.models.video import InvalidVideoError, Video
from vidsift.models.video_record import VideoProcessingStatus
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.services.summarization_service import SummarizationService


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


def handle_process(args, config: AppConfig):
    metadata_collector = MetadataCollector()
    orchestrator = VidsiftOrchestrator(
        channel_id_list=[""],
        config=config
    )
    try:
        vid: Video = metadata_collector.fetch_metadata(args.url)
    except InvalidVideoError:
        raise
    if args.download:
        downloader: VideoDownloader = VideoDownloader()
        orchestrator.execute_processing_step(
            vid=vid,
            step_type="download",
            success_decision="downloaded",
            starting_status=VideoProcessingStatus.DOWNLOADING,
            action=lambda: downloader.download(
                video_url=vid.url,
                output_path=Path(config.downloads.output_dir)
            )
        )
    else:
        transcript = orchestrator.fetch_transcript(
            vid=vid
        )
        if args.summarize:
            summarizer: SummarizationService = SummarizationService(config=config)
            orchestrator.execute_processing_step(
                vid=vid,
                step_type="summarize",
                success_decision="summarized",
                starting_status=VideoProcessingStatus.SUMMARIZING,
                action=lambda: summarizer.summarize(
                    raw_transcript=transcript,
                    vid=vid
                )
            )
        elif args.fetch_transcript:
            print(transcript)
        else:
            validation_result = orchestrator.validate_video(
                vid=vid,
                raw_transcript=transcript
            )
            orchestrator.take_action_on_video(
                vid=vid,
                video_validation_result=validation_result,
                transcript=transcript
            )
