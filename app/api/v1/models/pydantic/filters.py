from pydantic import BaseModel, field_validator, Field
import sys
import datetime


class BaseFilter(BaseModel):
    """Base filter model for common filter attributes."""
    limit: int = Field(default=100, ge=1, le=1000)

class DateRangeFilter(BaseModel):
    """Filter model for date range operations."""
    start_date: str = "1970-01-01"
    end_date: str = "2099-12-31"
    
    @field_validator('start_date', 'end_date')
    def validate_dates(cls, v):
        if not v:
            raise ValueError("Date cannot be empty")
        elif start_date > end_date:
            raise ValueError("Start date cannot be greater than end date")
        
        return v

class VideoFilter(BaseFilter):
    """Filter model for video operations."""
    video_ids: str = Field(default="")
    channel_id: str = Field(default="")
    channel_name: str = Field(default="")
    playlist_id: str = Field(default="")
    playlist_title: str = Field(default="")
    video_title: str = Field(default="")
    min_duration: datetime.timedelta = Field(default=datetime.timedelta(0))
    max_duration: datetime.timedelta = Field(default=datetime.timedelta.max)
    language: str = Field(default="")
    date_range: DateRangeFilter = Field(default_factory=DateRangeFilter)

class PlaylistFilter(BaseFilter):
    """Filter model for playlist operations."""
    channel_id: str = Field(default="")
    playlist_id: str = Field(default="")
    playlist_title: str = Field(default="")
    max_number_of_videos: int = Field(default=1000)
    min_number_of_videos: int = Field(default=0)
    status: str = Field(default="")
    date_range: DateRangeFilter = Field(default_factory=DateRangeFilter)

class ChannelFilter(BaseFilter):
    """Filter model for channel operations."""
    channel_id: str = Field(default="")
    channel_handle: str = Field(default="")
    channel_name: str = Field(default="")
    country: str = Field(default="")
    date_range: DateRangeFilter = Field(default_factory=DateRangeFilter)
    