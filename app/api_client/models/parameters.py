from dataclasses import dataclass, field
from typing import Iterable
from app.api_client.models.base import BaseParameters

@dataclass
class ChannelParameters(BaseParameters):
    """Parameters for fetching YouTube channel(s).
    
    Attributes:
        id: Channel ID(s) to fetch
        channel_handle: Channel handle (e.g., '@channelname') - maps to forUsername API param
        properties_details: Parts to include in response (e.g., 'snippet,statistics')
        max_results: Maximum number of results per page
    """
    channel_handle: str | None = None

@dataclass
class PlaylistParameters(BaseParameters):
    """Parameters for fetching YouTube playlist(s).
    
    Attributes:
        id: Playlist ID(s) to fetch
        channel_id: Channel ID to filter playlists
        properties_details: Parts to include in response
        max_results: Maximum number of results per page
    """
    channel_id: str | None = None

@dataclass
class PlaylistItemParameters(BaseParameters):
    """Parameters for fetching YouTube playlist item(s).
    
    Attributes:
        id: Playlist item ID(s) to fetch
        playlist_id: Playlist ID to fetch items from
        properties_details: Parts to include in response
        max_results: Maximum number of results per page
    """
    playlist_id: str | None = None

@dataclass
class VideoParameters(BaseParameters):
    """Parameters for fetching YouTube video(s).
    
    Attributes:
        id: Video ID(s) to fetch
        properties_details: Parts to include in response
        max_results: Maximum number of results per page
    """
    pass
    