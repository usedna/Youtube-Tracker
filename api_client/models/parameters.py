from dataclasses import dataclass
from api_client.models.base import BaseParameters

@dataclass
class ChannelParameters(BaseParameters):
    channel_handle: str | None = None

@dataclass
class PlaylistParameters(BaseParameters):
    channel_id: str | None = None

@dataclass
class PlaylistItemParameters(BaseParameters):
    playlist_id: str | None = None

@dataclass
class VideoParameters(BaseParameters):
    pass
    