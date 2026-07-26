"""
Videos API routes
"""
from datetime import datetime, date, time
import isodate
import logging

from fastapi import APIRouter, Depends, HTTPException
from api.v1.models.request import VideoRequestById, BatchResponse, APIResponse
from api.v1.database import DBSessionDep, get_session
from app.api.v1.models.media_db import Video
from api.v1.utils import service


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
            details = item.get("details") if isinstance(item, dict) else getattr(item, "details", None)
            if not details:
                continue

            video_id = details.get("video_id")
            if not video_id:
                continue

            # attempt to extract channel_id if present
            channel_id = details.get("channel_id") or item.get("channel_id")
            if not channel_id:
                # skip saving when required foreign key is missing
                logger.debug("Skipping save for video %s: missing channel_id", video_id)
                continue

            # parse uploaded date
            uploaded_at_str = details.get("uploaded_at") or details.get("uploadedAt")
            uploaded_at = None
            if uploaded_at_str:
                try:
                    uploaded_at = datetime.fromisoformat(uploaded_at_str.replace("Z", "")).date()
                except Exception:
                    try:
                        uploaded_at = date.fromisoformat(uploaded_at_str[:10])
                    except Exception:
                        uploaded_at = None

            # parse duration (string to time)
            duration_val = details.get("duration")
            duration_array = None
            if duration_val:
                try:
                    td = isodate.parse_duration(duration_val) if isinstance(duration_val, str) else duration_val
                    seconds = int(td.total_seconds())
                    h = (seconds // 3600) % 24
                    m = (seconds % 3600) // 60
                    s = seconds % 60
                    duration_array = [time(h, m, s)]
                except Exception:
                    duration_array = None

            
            obj = Video(
                video_id=video_id,
                channel_id=channel_id,
                etag=details.get("etag") or item.get("etag"),
                video_title=details.get("video_title"),
                duration=duration_array if duration_array is not None else [],
                video_description=details.get("video_description"),
                language=details.get("language"),
                tags=",".join(details.get("tags") or []) if isinstance(details.get("tags"), list) else details.get("tags"),
                dimension=details.get("dimension"),
                definition=details.get("definition"),
                paid=bool(details.get("paid")),
                captions=bool(details.get("caption") or details.get("captions")),
                uploade_at=uploaded_at if uploaded_at else date.today(),
            )
            session.add(obj)
            
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


@router.get("/info")
async def get_videos_info(
    session: DBSessionDep,
    limit: int = 100
    ):
    
    """Return videos stored in the database (up to 100 rows)."""
    rows = session.query(Video).limit(limit).all()
    result = []
    for r in rows:
        result.append({
            "video_id": r.video_id,
            "channel_id": r.channel_id,
            "etag": r.etag,
            "video_title": r.video_title,
            "duration": [d.isoformat() for d in (r.duration or [])],
            "video_description": r.video_description,
            "language": r.language,
            "tags": r.tags,
            "dimension": r.dimension,
            "definition": r.definition,
            "paid": r.paid,
            "captions": r.captions,
            "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
        })

    return {"count": len(result), "videos": result}