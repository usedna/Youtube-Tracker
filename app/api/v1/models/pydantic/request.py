"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, field_validator


class BaseRequest(BaseModel):
    """Base request model with common fields."""
    properties: list[str] | str | None = Field([], description="Properties to retrieve")
    max_results: int = Field(50, ge=1, le=50, description="Maximum results per request")

class ChannelRequestById(BaseRequest):
    """Request model for channel operations."""
    channel_ids: list[str] | None = Field([], description="list of YouTube channel IDs")

    @field_validator('channel_ids', mode='after')
    def validate_ids(cls, v, field):
        if v is not None and len(v) == 0:
            raise ValueError('channel_ids cannot be empty')
        return v

class ChannelRequestByHandle(BaseRequest):
    """Request model for channel operations."""
    channel_handles: list[str] | None = Field([], description="list of YouTube channel handles/usernames")
    
    @field_validator('channel_handles', mode='after')
    def validate_ids(cls, v, field):
        if v is not None and len(v) == 0:
            raise ValueError('channel_handles cannot be empty')
        return v

class PlaylistRequestByChannel(ChannelRequestById):
    """Request model for playlist operations."""
    fetch_all: bool = Field(False, description="Whether to fetch all pages")
        
class PlaylistRequestById(BaseRequest):
    """Request model for playlist operations."""
    playlist_ids: list[str] | None = Field([], description="list of YouTube playlist IDs")
    fetch_all: bool = Field(False, description="Whether to fetch all pages")
    
    @field_validator('playlist_ids', mode='after')
    def validate_ids(cls, v, field):
        if v is not None and len(v) == 0:
            raise ValueError('playlist_ids cannot be empty')
        return v    

class PlaylistItemRequestByPlaylist(PlaylistRequestById):
    pass


class VideoRequestById(BaseRequest):
    """Request model for video operations."""
    video_ids: list[str] | None = Field([], description="list of YouTube video IDs")
    
    @field_validator('video_ids', mode='after')
    def validate_ids(cls, v, field):
        if v is not None and len(v) == 0:
            raise ValueError('video_ids cannot be empty')
        return v


class APIResponse(BaseModel):
    """Generic API response model."""
    success: bool = Field(..., description="Whether the request was successful")
    data: list[dict] | None = Field(None, description="Response data")
    error: list[str] | None = Field(None, description="Error message if request failed")


class BatchResponse(BaseModel):
    """Response model for batch operations."""
    count: int | None = Field(None, description="Number of items returned")
    api_response: APIResponse = Field(..., description="API response details")
    
class WatchTimeResponse(BaseModel):
    """Response model for video info operations."""
    total_watch_time: str | None = Field("00:00:00", description="Total watch time of the videos")

class VideoResponse(BatchResponse, WatchTimeResponse):
    """Response model for video info operations."""
    pass