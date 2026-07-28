from dataclasses import dataclass
from datetime import timedelta
from app.api_client.models.base import BaseDataClass

@dataclass
class VideoBasicDetails(BaseDataClass):
    video_id: str
    channel_id: str
    video_title: str
    video_description: str
    uploaded_at: str

@dataclass
class VideoDetails(VideoBasicDetails):
    etag: str
    duration: timedelta
    language: str
    tags: list[str] | None
    dimension: str
    definition: str
    caption: bool
    paid: str

@dataclass
class Statistics(BaseDataClass):
    view_count: int
    like_count: int
    favorite_count: int
    comment_count: int

@dataclass
class Topics(BaseDataClass):
    categories: list[str]

@dataclass
class Status(BaseDataClass):
    upload_status: str
    privacy_status: str
    license: str
    embeddable: bool
    public_stats_viewable: bool
    made_for_kids: bool
    
@dataclass
class Video(BaseDataClass):
    details: VideoDetails
    statistics: Statistics
    topics: Topics
    status: Status
