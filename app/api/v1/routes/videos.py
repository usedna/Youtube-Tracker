"""
Videos API routes
"""

import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import and_
from api.v1.models.pydantic.request import VideoRequestById, BatchResponse, APIResponse, VideoResponse
from api.v1.database import DBSessionDep
from api.v1.models.db.media_db import Channel, Video, PlaylistsVideos, Playlist
from api.v1.models.pydantic.filters import VideoFilter
from api.v1.utils import service, unpack_video_details


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/by-ids", response_model=BatchResponse)
async def get_videos_by_ids(
    request: VideoRequestById,
    session: DBSessionDep,
) -> BatchResponse:
    """Get multiple videos by their IDs."""
    if not request.video_ids:
        raise HTTPException(status_code=400, detail="video_ids is required")

    try:
        result = service.get_videos_by_id(
            video_ids=request.video_ids,
            properties=request.properties,
            max_results=request.max_results
        )
        # Persist videos to DB (upsert) when possible
        for item in result:
            details = item.get("details")
            if not details:
                continue

            checked_items = set()
            for video_item in unpack_video_details(details):
                
                if video_item["channel_id"] not in checked_items:
                    obj_item = {"channel_id": video_item["channel_id"]}
                    Channel.get_or_create(session, **obj_item)
                    checked_items.add(video_item["video_id"])

                Video.update_or_create(session, fkey=["video_id"], **video_item)
            
        try:
            session.commit()
        except Exception:
            session.rollback()

        return BatchResponse(api_response=APIResponse(success=True,
                                                      data=result),
                             count=len(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")

@router.put("/auto", response_model=APIResponse)
async def auto_update_videos(
    session: DBSessionDep,
    limit: int = 100) -> APIResponse:
    """Automatically update videos in the database."""
    try:
        # Fetch videos from the database
        videos = session.query(Video).limit(limit).all()
        video_ids = [video.video_id for video in videos]

        if not video_ids:
            return APIResponse(success=True, data="No videos to update.")

        # Fetch updated video details from the service
        result = service.get_videos_by_id(video_ids=video_ids)

        # Update videos in the database
        for item in result:
            
            video_item = unpack_video_details(item)
            Video.update_or_create(session, fkey=["video_id"], **video_item)

        try:
            session.commit()
        except Exception:
            session.rollback()

        return APIResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-update videos: {str(e)}")

@router.get("/info", response_model=VideoResponse)
async def get_videos_info(
    session: DBSessionDep,
    filters: Annotated[VideoFilter, Query()],
    ):
    
    """Return videos stored in the database (up to 100 rows)."""
    try:
        
        if filters.playlist_id or filters.playlist_title:
            table = session.query(Video.__table__) \
                           .join(PlaylistsVideos) \
                           .join(Playlist.__table__) \
                           .where(Playlist.playlist_title.ilike(f"%{filters.playlist_title}%"))

        elif filters.channel_id or filters.channel_name:
            table = session.query(Video.__table__) \
                           .join(Channel.__table__) \
                           .where(Channel.channel_name.ilike(f"%{filters.channel_name}%"))

        else:
            table = session.query(Video.__table__)
            
        rows = table.filter(and_(Video.video_id.ilike(f"%{filters.video_ids}%"),
                      Video.channel_id.ilike(f"%{filters.channel_id}%"),
                      Video.video_title.ilike(f"%{filters.video_title}%"),
                      Video.duration >= filters.min_duration,
                      Video.duration <= filters.max_duration,
                      Video.language.ilike(f"%{filters.language}%"),
                      Video.uploaded_at > filters.date_range.start_date,
                      Video.uploaded_at < filters.date_range.end_date
                  )).limit(filters.limit).all()
        result = []
        total_time = timedelta(0)
        for r in rows:
            r = r._mapping
            total_time += r["duration"]
            result.append(r)

        return VideoResponse(total_watch_time=str(total_time),
                             count=len(result),
                             api_response=APIResponse(success=True,
                                                      data=result),
                            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")
