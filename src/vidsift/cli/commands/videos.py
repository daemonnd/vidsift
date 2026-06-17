from rich.console import Console

from vidsift.features.video_processing.repository import \
    VideoProcessingRepository


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

    video_set_status.set_defaults(
        func=handle_videos_set_status
    )

    return videos_parser

def handle_videos_list(args, config):
    repo = VideoProcessingRepository()
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
    repo = VideoProcessingRepository()
    try:
        if args.video_id and args.status:
            repo.set_status(args.video_id, args.status)
    finally:
        repo.close()

