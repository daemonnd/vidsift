from rich.console import Console

from vidsift.features.video_processing.repository import \
    VideoProcessingRepository
from vidsift.models.video_record import VideoProcessingStatus


def register_videos(subparsers):
    videos_parser = subparsers.add_parser(
        "videos",
        help="Edit view or video processed videos",
    )
    videos_subparsers = videos_parser.add_subparsers(
        dest="videos_command",
        required=True
    )
    video_list = videos_subparsers.add_parser(
        "list",
        help="list already processed videos",
    )
    video_list.add_argument(
        "-s", "--status",
        help="filter by processing status ('downloading', 'summarizing', 'done', 'failed', 'validating'",
        choices=["downloading", "summarizing", "done", "failed", "validating"]
    )

    video_list.set_defaults(
        func=handle_videos_list
    )

    video_set_status = videos_subparsers.add_parser(
        "set-status",
        help="Set the status of <video id> to <status>"
    )
    video_set_status.add_argument(
        "--video-id",
        help="ID of the target video"
    )
    video_set_status.add_argument(
        "--status",
        help="Target status of video",
        choices=["downloading", "summarizing", "done", "failed", "validating"]
    )
    video_set_status.add_argument(
        "--reset-failed-attempts",
        help="Set the failed attempts amount to 0 (only recommended if setting the status to done or testing)",
        action="store_true"
    )

    video_set_status.set_defaults(
        func=handle_videos_set_status
    )

    videos_delete_one = videos_subparsers.add_parser(
        "delete-video",
        help="Delete a video from the database so it can be reprocessed"
    )
    videos_delete_one.add_argument(
        "--video-id",
        help="ID of the target video",
        required=True
    )
    videos_delete_one.set_defaults(func=handle_videos_delete)

    return videos_parser

def handle_videos_list(args, config):
    repo = VideoProcessingRepository(config=config)
    try:
        if args.status:
            videos = repo.get_by_status(args.status)
        else:
            videos = repo.get_all()

        console = Console()

        for video in videos:
            console.print(video)
    finally:
        repo.close()

def handle_videos_set_status(args, config):
    repo = VideoProcessingRepository(config=config)
    match args.status: # args.status can only be "downloading", "summarizing", "validating", "failed", "done", because that is set in the choices
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
    try:
        if args.video_id and args.status:
            if args.reset_failed_attempts:
                repo.set_status(args.video_id, target_status, reset_attempts=True)
            else:
                repo.set_status(args.video_id, target_status, reset_attempts=False)

    finally:
        repo.close()

def handle_videos_delete(args, config):
    repo = VideoProcessingRepository(config=config)
    try:
        repo.del_row(
            video_id=args.video_id
        )
    finally:
        repo.close()

