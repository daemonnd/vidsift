from vidsift.config.errors import ConfigError
from vidsift.config.loader import load_config
from vidsift.features.video_processing.repository import \
    VideoProcessingRepository


def complete_channel_ids(prefix, parsed_args, **kwargs) -> list[str]:
    try:
        if parsed_args.config:
            config = load_config(parsed_args.config)
        else:
            config = load_config()
        return [
            channel.id
            for channel in config.channels
            if channel.id.startswith(prefix)
        ]
    except (ConfigError, OSError):
        return []

def complete_video_ids(prefix, parsed_args, **kwargs) -> list[str]:
    try:
        if parsed_args.config:
            config = load_config(parsed_args.config)
        else:
            config = load_config()
        video_db = VideoProcessingRepository(config)
        return [
            processing_record.video_id
            for processing_record in video_db.get_all()
            if processing_record.video_id.startswith(prefix)
        ]
    except (ConfigError, OSError):
        return []
