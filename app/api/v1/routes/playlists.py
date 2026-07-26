"""
Playlists API routes
"""
from datetime import datetime, date
import logging

from fastapi import APIRouter, Depends, HTTPException
from api.v1.models.request import PlaylistRequestByChannel, PlaylistRequestById,PlaylistItemRequestByPlaylist, BatchResponse, APIResponse
from api.v1.database import DBSessionDep, get_session
from api.v1.models.media_db import Channel, Playlist, PlaylistsVideos, Video
from api.v1.utils import service, unpack_playlists, unpack_playlist_items


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/by-channel-ids", response_model=BatchResponse)
async def get_playlists_by_channel_ids(
    request: PlaylistRequestByChannel,
    session: DBSessionDep,
) -> BatchResponse:
    """Get all playlists for specified channel IDs."""
    if not request.channel_ids:
        raise HTTPException(status_code=400, detail="channel_ids is required")

    try:
        # Call service per channel to be able to associate playlists with the channel
        result = service.get_playlists_by_channel_id(
            channel_ids=request.channel_ids,
            properties=request.properties,
            max_results=request.max_results,
            fetch_all=request.fetch_all
        )

        # Persist playlists for this channel
        for item in result:
            playlists = item.get("playlists") if isinstance(item, dict) else getattr(item, "playlists", None)
            if not playlists:
                continue
            
            playlists = [p for p in unpack_playlists(playlists)]
            channel_ids = set([p.get("channel_id") for p in playlists if p.get("channel_id")])
            channel_ids = [{"channel_id": cid} for cid in channel_ids]
            Channel.get_or_create_many(session, channel_ids)

            obj = [Playlist(**playlist) for playlist in playlists]
            session.bulk_save_objects(obj)

        try:
            session.commit()
            logger.info(f"Successfully committed {len(obj)} playlists to DB")
        except Exception:
            session.rollback()
            logger.exception("Failed committing playlists to DB")

        return BatchResponse(
            api_response=APIResponse(
                success=True,
                data=result
            ),
            count=len(obj)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch playlists: {str(e)}")
    

@router.post("/by-ids", response_model=BatchResponse)
async def get_playlists_by_ids(
    request: PlaylistRequestById,
    session: DBSessionDep,
) -> BatchResponse:
    """Get playlists for specified playlist IDs."""
    if not request.playlist_ids:
        raise HTTPException(status_code=400, detail="playlist_ids is required")

    try:
        result = service.get_playlists_by_playlist_id(
            playlist_ids=request.playlist_ids,
            properties=request.properties,
            max_results=request.max_results,
        )

        # Persist playlists to DB (upsert)
        for item in result:
            playlists = item.get("playlists") if isinstance(item, dict) else getattr(item, "playlists", None)
            if not playlists:
                continue
            
            playlists = [p for p in unpack_playlists(playlists)]
            channel_ids = set([p.get("channel_id") for p in playlists if p.get("channel_id")])
            channel_ids = [{"channel_id": cid} for cid in channel_ids]
            Channel.get_or_create_many(session, channel_ids)
            
            obj = [Playlist(**playlist) for playlist in playlists]
            session.bulk_save_objects(obj)
            
        try:
            session.commit()
            logger.info(f"Successfully committed {len(obj)} playlists to DB")
        except Exception:
            session.rollback()
            logger.exception("Failed committing playlists to DB")
            
        return BatchResponse(
            api_response=APIResponse(
                success=True,
                data=result
            ),
            
            count=len(obj)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch playlists: {str(e)}")
            


@router.post("/items/by-playlist-ids", response_model=BatchResponse)
async def get_playlist_items_by_playlist_ids(
    request: PlaylistItemRequestByPlaylist,
    session: DBSessionDep,
    ) -> BatchResponse:
    
    """Get all playlist items for specified playlist IDs."""
    if not request.playlist_ids:
        raise HTTPException(status_code=400, detail="playlist_ids is required")

    try:
        result = service.get_playlist_items_by_playlist_id(
            playlist_ids=request.playlist_ids,
            properties=request.properties,
            max_results=request.max_results,
            fetch_all=request.fetch_all
        )

        for item in result:
            playlist_items = item.get("items") if isinstance(item, dict) else getattr(item, "items", None)
            if not playlist_items:
                continue
            
            checked_items = set()
            playlist_items = [pi for pi in unpack_playlist_items(playlist_items)]
            for pi in playlist_items:
                channel_id = pi.get("video").get("channel_id")
                playlist_id = pi.get("item").get("playlist_id")
                video_id = pi.get("video").get("video_id")
                
                if checked_items.issuperset({channel_id, playlist_id, video_id}):
                    continue
                
                checked_items.add(channel_id)
                checked_items.add(playlist_id)
                checked_items.add(video_id)
                
                obj_item = {"channel_id": channel_id}
                Channel.get_or_create(session, **obj_item)
                
                obj_item.update({"playlist_id": playlist_id})
                Playlist.get_or_create(session, **obj_item)
                
                Video.get_or_create(session, fkey=["video_id"], **pi.get("video"))

                pl_vid = {"playlist_id": playlist_id, 
                          "video_id": pi.get("video").get("video_id"),
                          "position": pi.get("item").get("position"),
                          "published_at": pi.get("item").get("published_at")}
                PlaylistsVideos.get_or_create(session, **pl_vid)

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
        raise HTTPException(status_code=500, detail=f"Failed to fetch playlist items: {str(e)}")


@router.get("/info")
async def get_playlists_info(
    session: DBSessionDep,
    limit: int = 100
    ):
    
    """Return playlists stored in the database (up to 100 rows)."""
    rows = session.query(Playlist).limit(limit).all()
    result = [{
            "playlist_id": r.playlist_id,
            "channel_id": r.channel_id,
            "playlist_title": r.playlist_title,
            "description": r.description,
            "videos_count": r.videos_count,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in rows]

    return {"count": len(result), "playlists": result}

@router.get("/items/info")
async def get_playlist_items_info(
    session: DBSessionDep,
    limit: int = 100
    ):
    
    """Return playlist items stored in the database (up to 100 rows)."""
    rows = session.query(PlaylistsVideos).limit(limit).all()
    result = [{
            "playlist_id": r.playlist_id,
            "video_id": r.video_id,
            "position": r.position,
            "published_at": r.published_at.isoformat() if r.published_at else None,
            } for r in rows]

    return {"count": len(result), "playlist_items": result}