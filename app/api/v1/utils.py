"""
Dependencies for FastAPI routes
"""
from datetime import datetime, date
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
    
    details = item.get("details") if isinstance(item, dict) else getattr(item, "details", None)
    if not details:
        return None

    channel_id = details.get("channel_id")
    if not channel_id:
        return None

    created_at = details.get("created_at")
    if created_at:
        created_at = get_timestamp_from_iso(created_at)

    return {
        "channel_id": channel_id,
        "channel_handle": details.get("channel_handle"),
        "etag": details.get("etag"),
        "upload_id": details.get("upload_id"),
        "channel_name": details.get("channel_name"),
        "channel_description": details.get("channel_description"),
        "created_at": created_at if created_at else date.today(),
        "country": details.get("country"),
    }

def unpack_playlists(playlists: dict) -> dict:
    """Unpack playlist details from the API response."""
    
    for playlist in playlists:
        details = playlist.get("details")
        if not details:
            continue
        
        status = playlist.get("status")
        playlist_id = details.get("playlist_id")
        channel_id = details.get("channel_id")
        if not playlist_id or not channel_id:
            continue
        
        created_at = details.get("created_at")
        
        if created_at:
            created_at = get_timestamp_from_iso(created_at)

        yield {
            "playlist_id": playlist_id,
            "channel_id": channel_id,
            "playlist_title": details.get("playlist_title"),
            "description": details.get("description"),
            "videos_count": details.get("videos_count") or 0,
            "created_at": created_at if created_at else date.today(),
            "status": status.get("privacy_status"),
        }

def unpack_playlist_items(items: dict) -> dict:
    """Unpack playlist item details from the API response."""
    
    for item in items:
        video_details = item.get("details")
        item_details = item.get("item")
        if not video_details and not item_details:
            continue
        
        video_id = video_details.get("video_id")
        item_id = item_details.get("item_id")
        playlist_id = item_details.get("playlist_id")
        channel_id = video_details.get("channel_id")
        
        if not video_id and not item_id and not playlist_id and not channel_id:
            continue
        
        uploaded_at = video_details.get("uploaded_at")
        published_at = item_details.get("published_at")
        
        if published_at:
            published_at = get_timestamp_from_iso(published_at)
        
        if uploaded_at:
            uploaded_at = get_timestamp_from_iso(uploaded_at)    

        yield {
            "video": {
                "video_id": video_id,
                "channel_id": channel_id,
                "video_title": video_details.get("video_title"),
                "video_description": video_details.get("video_description"),
                "uploaded_at": uploaded_at if uploaded_at else date.today(),
            },
            "item": {
                "item_id": item_id,
                "playlist_id": playlist_id,
                "position": item_details.get("position") or 0,
                "published_at": published_at,
            },
        }

service = get_youtube_service()
 