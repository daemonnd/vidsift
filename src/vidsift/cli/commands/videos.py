import logging

from rich.console import Console

from vidsift.cli.autocomplete import complete_channel_ids, complete_video_ids
from vidsift.features.video_processing.errors import VideoProcessingError
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.models.video_record import VideoProcessingStatus
from vidsift.shared.logging.log_event_fields import LogEvent
from vidsift.shared.paths import PROCESSED_VIDEOS_DB

logger = logging.getLogger(__name__)


def register_videos(subparsers):
    videos_parser = subparsers.add_parser(
        "videos",
        help="Edit or view processed and processing videos",
    )
    videos_parser.add_argument(
        "--show-db-path",
        help="Show the absolute path to the video processing database. That is also possible by simply using vidsift videos",
        action="store_true",
    )
    videos_parser.set_defaults(func=handle_db_path_print)
    videos_subparsers = videos_parser.add_subparsers(
        dest="videos_command",
    )
    video_list = videos_subparsers.add_parser(
        "list",
        help="list already processed videos",
    )
    video_list.add_argument(
        "-s",
        "--status",
        help="filter by processing status ('downloading', 'summarizing', 'done', 'failed', 'validating'",
        choices=["downloading", "summarizing", "done", "failed", "validating", ],
    )

    video_list.add_argument(
        "--video-id", help="only show the db entry with the matching video id"
    ).completer = complete_video_ids

    video_list.add_argument(
        "--channel-id", help="only show the db entries with the matching channel id"
    ).completer = complete_channel_ids

    video_list.set_defaults(func=handle_videos_list)

    video_set_status = videos_subparsers.add_parser(
        "set-status", help="Set the status of <video id> to <status>"
    )
    video_set_status.add_argument("video_id", help="ID of the target video").completer = complete_video_ids
    video_set_status.add_argument(
        "--status",
        help="Target status of video (default: done)",
        choices=[
            "downloading",
            "summarizing",
            "done",
            "failed",
            "validating",
            "data_enriching",
        ],
        default="done"
    )
    video_set_status.add_argument(
        "--reset-failed-attempts",
        help="Set the failed attempts amount to 0 (only recommended if setting the status to done or testing)",
        action="store_true",
    )

    video_set_status.set_defaults(func=handle_videos_set_status)

    videos_delete_one = videos_subparsers.add_parser(
        "rm", help="Delete a video from the database so it can be reprocessed"
    )
    videos_delete_one.add_argument(
        "video_id", help="ID of the target video"
    ).completer = complete_video_ids
    videos_delete_one.set_defaults(func=handle_videos_delete)

    return videos_parser


def handle_videos_list(args, config, run_id):
    repo = VideoProcessingRepository(config=config)
    console = Console()
    try:
        if args.status:
            videos = repo.get_by_status(args.status)
        elif args.video_id:
            result = repo.get(video_id=args.video_id)
            if result is None:
                console.print("Error: no rows found for search criteria")
            console.print(result)
            return
        elif args.channel_id:
            videos = repo.get_by_channelid(channel_id=args.channel_id)
        else:
            videos = repo.get_all()

        for video in videos:
            console.print(video)
    except VideoProcessingError as e:
        logger.exception(f"Error while listing videos: {e}", extra={"event": LogEvent.VIDEO_PROCESSING_ERROR})
    finally:
        repo.close()


def handle_videos_set_status(args, config, run_id):
    repo = VideoProcessingRepository(config=config)
    match args.status:  # args.status can only be "downloading", "summarizing", "validating", "failed", "done", because that is set in the choices
        case "downloading":
            target_status = VideoProcessingStatus.DOWNLOADING
        case "summarizing":
            target_status = VideoProcessingStatus.SUMMARIZING
        case "validating":
            target_status = VideoProcessingStatus.VALIDATING
        case "failed":
            target_status = VideoProcessingStatus.FAILED
        case "done":
            target_status = VideoProcessingStatus.DONE
        case "data_enriching":
            target_status = VideoProcessingStatus.DATA_ENRICHING
        case _:
            raise ValueError(f"Invalid status: {args.status}")
    try:
        if args.video_id and args.status:
            if args.reset_failed_attempts:
                repo.set_status(args.video_id, target_status, reset_attempts=True)
            else:
                repo.set_status(args.video_id, target_status, reset_attempts=False)
    except VideoProcessingError as e:
        logger.exception(f"Error while trying to set the status of video id '{args.video_id}' to status '{args.status}': {str(e)}", extra={"event": LogEvent.VIDEO_PROCESSING_ERROR})

    finally:
        repo.close()


def handle_videos_delete(args, config, run_id):
    repo = VideoProcessingRepository(config=config)
    try:
        repo.del_row(video_id=args.video_id)
    except VideoProcessingError as e:
        logger.exception(f"Error while trying to delete video with video id '{args.video_id}': {e}", extra={"event": LogEvent.VIDEO_PROCESSING_ERROR})
    finally:
        repo.close()


def handle_db_path_print(args, config, run_id):
    print(PROCESSED_VIDEOS_DB)
