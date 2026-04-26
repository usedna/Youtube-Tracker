from dataclasses import dataclass
from api_client.models.base import BaseDataClass


@dataclass
class Details(BaseDataClass):
    channel_id: str
    uploads_id: str
    channel_name: str
    channel_handle: str
    etag: str
    channel_description: str
    created_at: str
    country: str

@dataclass
class Statistics(BaseDataClass):
    views_count: int
    subscribers_count: int
    is_subscriber_count_hidden: bool
    videos_count: int

@dataclass
class Topics(BaseDataClass):
    topic_ids: list[str]
    topic_categories: list[str]

@dataclass
class Thumbnails(BaseDataClass):
    default: dict[str, any]
    medium: dict[str, any]
    high: dict[str, any]

@dataclass
class BannerImage(BaseDataClass):
    banner_image_url: str
    
@dataclass
class Keywords(BaseDataClass):
    keywords: list[str] | str

@dataclass
class Status(BaseDataClass):
    privacy: str
    is_linked: bool
    long_uploads_status: str
    made_for_kids: bool = False
    
@dataclass
class Channel(BaseDataClass):
    details: Details
    statistics: Statistics
    topics: Topics
    thumbnails: Thumbnails
    banner_image: BannerImage
    keywords: Keywords
    status: Status