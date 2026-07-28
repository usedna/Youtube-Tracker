"""
Videos API routes
"""

from datetime import timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException
from api.v1.models.request import VideoRequestById, BatchResponse, APIResponse
from api.v1.database import DBSessionDep, get_session
from app.api.v1.models.media_db import Channel, Video
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

        return BatchResponse(
            api_response=APIResponse(
                success=True,
                data=result
            ),
            count=len(result) if isinstance(result, list) else 1
        )
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

@router.get("/info")
async def get_videos_info(
    session: DBSessionDep,
    limit: int = 100
    ):
    
    """Return videos stored in the database (up to 100 rows)."""
    rows = session.query(Video).limit(limit).all()
    result = []
    total_time = timedelta(0)
    for r in rows:
        total_time += r.duration
        result.append({
            "video_id": r.video_id,
            "channel_id": r.channel_id,
            "etag": r.etag,
            "video_title": r.video_title,
            "duration": r.duration,
            "video_description": r.video_description,
            "language": r.language,
            "tags": r.tags,
            "dimension": r.dimension,
            "definition": r.definition,
            "paid": r.paid,
            "captions": r.captions,
            "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
        })

    return {"count": len(result), "total_watch_time": str(total_time), "videos": result}