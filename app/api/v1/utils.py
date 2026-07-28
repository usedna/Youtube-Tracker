"""
Dependencies for FastAPI routes
"""
from datetime import datetime, date, timedelta
from fastapi import HTTPException
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

try:
    from app.api_client.service.youtube_service import YoutubeDataService
    from .config import settings
except ImportError as e:
    raise ImportError(f"Failed to import YouTube service: {e}")

def get_timestamp_from_iso(iso_str: str) -> datetime:
    try:
        iso_str = datetime.fromisoformat(iso_str.replace("Z", "")).date()
    except Exception:
        try:
            iso_str = date.fromisoformat(iso_str[:10])
        except Exception:
            iso_str = None
    return iso_str


def get_interval_from_str(iso_str: str) -> timedelta:
    try:
        hours, minutes, seconds = map(int, iso_str.split(':'))
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except Exception:
        return timedelta(0)


def get_youtube_service() -> YoutubeDataService:
    """Dependency to get YouTube service instance."""
    
    try:
        service = YoutubeDataService.create_service(
            api_key=settings.API_KEY,
            auth_file=settings.AUTH_FILE, 
            scopes=settings.SCOPES
        )
        
        return service
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize YouTube service: {str(e)}"
        )
        
def unpack_channel_details(item: dict) -> dict:
    """Unpack channel details from the API response."""
    
    details = item.get("details")
    if not details:
        return None

    channel_id = details["channel_id"]
    if not channel_id.strip():
        return None

    created_at = details["created_at"]
    if created_at:
        created_at = get_timestamp_from_iso(created_at)

    return {
        "channel_id": channel_id,
        "channel_handle": details["channel_handle"],
        "etag": details["etag"],
        "upload_id": details["upload_id"],
        "channel_name": details["channel_name"],
        "channel_description": details["channel_description"],
        "created_at": created_at if created_at else date.today(),
        "country": details["country"],
    }

def unpack_playlists(playlists: dict) -> dict:
    """Unpack playlist details from the API response."""
    
    for playlist in playlists:
        details = playlist.get("details")
        if not details:
            continue
        
        status = playlist["status"]
        playlist_id = details["playlist_id"]
        channel_id = details["channel_id"]
        if not playlist_id.strip() or not channel_id.strip():
            continue
        
        created_at = details["created_at"]
        
        if created_at:
            created_at = get_timestamp_from_iso(created_at)

        yield {
            "playlist_id": playlist_id,
            "channel_id": channel_id,
            "playlist_title": details["playlist_title"],
            "description": details["description"],
            "videos_count": details["videos_count"],
            "created_at": created_at if created_at else date.today(),
            "status": status["privacy_status"],
        }

def unpack_playlist_items(items: dict) -> dict:
    """Unpack playlist item details from the API response."""
    
    for item in items:
        video_details = item.get("details")
        item_details = item.get("item")
        if not video_details and not item_details:
            continue
        
        video_id = video_details["video_id"]
        item_id = item_details["item_id"]
        playlist_id = item_details["playlist_id"]
        channel_id = video_details["channel_id"]
        
        if not video_id.strip() and not item_id.strip() and not playlist_id.strip() and not channel_id.strip():
            continue
        
        uploaded_at = video_details.get("uploaded_at")
        published_at = item_details.get("published_at")
        
        if not published_at.strip():
            published_at = get_timestamp_from_iso(published_at)
        
        if not uploaded_at.strip():
            uploaded_at = get_timestamp_from_iso(uploaded_at)    

        yield {
            "video": {
                "video_id": video_id,
                "channel_id": channel_id,
                "video_title": video_details["video_title"],
                "video_description": video_details["video_description"],
                "uploaded_at": uploaded_at if uploaded_at else date.today(),
            },
            "item": {
                "item_id": item_id,
                "playlist_id": playlist_id,
                "position": item_details["position"],
                "published_at": published_at,
            },
        }

def unpack_video_details(item: dict) -> dict:
    """Unpack video details from the API response."""
    
    details = item.get("details")
    if not details:
        return None

    video_id = details["video_id"]
    if not video_id.strip():
        return None

    uploaded_at = details["uploaded_at"]
    if uploaded_at:
        uploaded_at = get_timestamp_from_iso(uploaded_at)
        
    duration = get_interval_from_str(details["duration"])

    return {
        "video_id": video_id,
        "channel_id": details["channel_id"],
        "etag": details["etag"],
        "video_title": details["video_title"],
        "duration": duration,
        "video_description": details["video_description"],
        "language": details["language"],
        "tags": details["tags"],
        "dimension": details["dimension"],
        "definition": details["definition"],
        "paid": bool(details.get("paid")),
        "captions": bool(details.get("caption") or details.get("captions")),
        "uploaded_at": uploaded_at if uploaded_at else date.today(),
    }

service = get_youtube_service()
 