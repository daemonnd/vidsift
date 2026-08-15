import logging
from pathlib import Path

import argcomplete

from vidsift.config.models import AppConfig
from vidsift.features.download.downloader import VideoDownloader
from vidsift.ingestion.metadata_collector import MetadataCollector
from vidsift.models.video import InvalidVideoError, Video
from vidsift.pipeline.vidsift_pipeline import VidsiftOrchestrator
from vidsift.services.summarization_service import SummarizationService
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.run_manager import RunManager


def register_process(subparsers):
    process_parser = subparsers.add_parser(
        "process",
        help="Process a certain URL ",
        usage="""The video url is required.
        Only one of --summarize and --download can be used and is required.
        --fake-download is only compatible with --download
        """
        )
    exclusive_process_parser_group = process_parser.add_mutually_exclusive_group(required=True)
    process_parser.add_argument(
        "url",
        help="""Process a specific video
        The process command is not recommended for automations because 
        transcript fetching for example will not only output the transcript but also the console logs
        """,
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
        help="""Fetch the transcript of the selected video
        It is recommended to run it rather like that to only get the transcript out:
        vidsift --loglevel ERROR process <url> --fetch-transcript
        Because else logs will also be printed to stdout.
        Additionally, it is highly recommended to turn off yt-dlp logs in order to 
        get only the transcript to stdout.
        """,
        action="store_true"
    )
    process_parser.add_argument( # to make it not exclusive with download, but exclusive with summarize and fetch-transcript
        "--fake-download",
        nargs='?',
        const=True,  # value when flag is used WITHOUT an argument
        default=None,  # value when flag is NOT used at all
        help="""Simulate the download of videos without actually downloading them.
        Instead, the url of the video to the filepath specified in the config file, 
        to override that config file value, use
        --fake-download-path /path/to/fake/download/file.
        The default value for that is the download targed dir / 'to_watch.md' """,
    ).completer = argcomplete.completers.FilesCompleter
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
            video_id = VideoIDExtractor().extract_id(args.url)
            downloader: VideoDownloader = VideoDownloader(config=config)
            if not config.downloads.fake_download:
                logger.info(
                    f"Starting manual download with url {args.url}",
                    extra={
                        "event": LogEvent.MANUAL_DOWNLOAD_RUN_STARTED,
                        "video_id": video_id
                    }
                )
                downloader.download(
                    video_url=args.url,
                    output_path=Path(config.downloads.output_dir)
                )
                return
            else:
                logger.info(
                    f"Starting manual fake download with url {args.url}",
                    extra={
                        "event": LogEvent.MANUAL_FAKE_DOWNLOAD_RUN_STARTED,
                        "video_id": video_id,
                        "output_path": config.downloads.output_path
                    }
                )
                downloader.download(
                    video_url=args.url,
                    output_path=Path(config.downloads.output_dir)
                )
                return



        metadata_collector = MetadataCollector(config=config)
        try:
            vid: Video = metadata_collector.fetch_metadata(args.url)
        except InvalidVideoError as e:
            logger.exception(f"InvalidVideoError: {str(e)}")
        else:
            try:
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
                else:
                    print(transcript)
            except Exception as e:
                logger.exception(
                    f"{type(e).__name__}: {str(e)}",
                    extra={
                        "video_id": vid.video_id,
                        "channel_id": vid.channel_id
                    }
                )
                raise
    finally:
        run_manager.end_run()
