from rich.console import Console

from vidsift.features.video_processing.repository import \
    VideoProcessingRepository


def handle_videos_list(self, args):
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

def handle_videos_set_status(self, args):
    repo = VideoProcessingRepository()
    try:
        if args.video_id and args.status:
            repo.set_status(args.video_id, args.status)
    finally:
        repo.close()

