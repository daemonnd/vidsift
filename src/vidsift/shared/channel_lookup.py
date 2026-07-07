from vidsift.config.models import ChannelConfig


def get_channel_lookup(config: list[ChannelConfig]):
    channel_lookup: dict[str, ChannelConfig] = {}
    channels: list[ChannelConfig] = config
    channel_lookup = {
        channel.id: channel
        for channel in channels
    }
    return channel_lookup
