from vidsift.config.errors import ConfigError
from vidsift.config.loader import load_config


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

