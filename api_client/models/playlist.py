from dataclasses import dataclass
from api_client.models.channel import Thumbnails
from api_client.models.video import VideoBasicDetails
from api_client.models.base import BaseDataClass


@dataclass
class Details(BaseDataClass):
    playlist_id: str
    playlist_title: str
    description: str
    videos_count: int
    created_at: str

@dataclass
class ItemThumbnails(Thumbnails):
    standard: dict
    maxres: dict

@dataclass
class Status(BaseDataClass):
    privacy_status: str
    
@dataclass
class Playlist(BaseDataClass):
    details: Details
    thumbnails: ItemThumbnails
    status: Status

@dataclass
class Playlists(BaseDataClass):
    playlists: list[Playlist]
    playlists_count: int

@dataclass
class ItemDetails(BaseDataClass):
    item_id: str
    position: int
    published_at: str

@dataclass
class Item(BaseDataClass):
    video_details: VideoBasicDetails
    item: ItemDetails
    thumbnails: ItemThumbnails
    

@dataclass
class PlaylistItems(BaseDataClass):
    items: list[Item]
    items_count: int