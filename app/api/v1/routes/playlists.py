"""
Playlists API routes
"""
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import and_
from api.v1.models.pydantic.request import PlaylistRequestByChannel, PlaylistRequestById, PlaylistItemRequestByPlaylist, BatchResponse, APIResponse
from api.v1.database import DBSessionDep
from api.v1.models.db.media_db import Channel, Playlist, PlaylistsVideos, Video
from api.v1.models.pydantic.filters import PlaylistFilter
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

        count = 0
        for item in result:
            playlists = item.get("playlists")
            if not playlists:
                continue
            
            checked_items = set()
            for playlist in unpack_playlists(playlists):
                
                if playlist["channel_id"] not in checked_items:
                    obj_item = {"channel_id": playlist["channel_id"]}
                    Channel.get_or_create(session, **obj_item)
                    checked_items.add(playlist["channel_id"])

                Playlist.update_or_create(session, fkey=["playlist_id"], **playlist)
                count += 1
        try:
            session.commit()
            logger.info(f"Successfully committed {count} playlists to DB")
        except Exception:
            session.rollback()
            logger.exception("Failed committing playlists to DB")

        return BatchResponse(api_response=APIResponse(success=True,
                                                      data=result),
                             count=count)
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

        count = 0
        for item in result:
            playlists = item.get("playlists")
            if not playlists:
                continue
                        
            checked_items = set()
            for playlist in unpack_playlists(playlists):
                if playlist["channel_id"] not in checked_items:
                    obj_item = {"channel_id": playlist["channel_id"]}
                    Channel.get_or_create(session, **obj_item)
                    checked_items.add(playlist["channel_id"])
            
                Playlist.update_or_create(session, fkey=["playlist_id"], **playlist)
                count += 1

        try:
            session.commit()
            logger.info(f"Successfully committed {count} playlists to DB")
        except Exception:
            session.rollback()
            logger.exception("Failed committing playlists to DB")
            
        return BatchResponse(api_response=APIResponse(success=True,
                                                      data=result),
                             count=count)
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

        count = 0
        for item in result:
            playlist_items = item.get("items")
            if not playlist_items:
                continue
            
            checked_items = set()
            for pi in unpack_playlist_items(playlist_items):
                pl_vid = {"playlist_id": pi["item"]["playlist_id"], 
                          "video_id": pi["video"]["video_id"],
                          "position": pi["item"]["position"],
                          "published_at": pi["item"]["published_at"]}

                channel_id = pi["video"]["channel_id"]
                
                if checked_items.issuperset({channel_id, pl_vid["playlist_id"], pl_vid["video_id"]}):
                    PlaylistsVideos.update_or_create(session, fkey=["playlist_id", "video_id"], **pl_vid)
                    continue
                
                if channel_id not in checked_items:
                    obj_item = {"channel_id": channel_id}
                    Channel.get_or_create(session, **obj_item)
                    checked_items.add(channel_id)
                
                if pl_vid["playlist_id"] not in checked_items:
                    obj_item.update({"playlist_id": pl_vid["playlist_id"]})
                    Playlist.get_or_create(session, **obj_item)
                    checked_items.add(pl_vid["playlist_id"])
                    
                if pl_vid["video_id"] not in checked_items:
                    Video.get_or_create(session, fkey=["video_id"], **pi.get("video"))
                    checked_items.add(pl_vid["video_id"])
                
                PlaylistsVideos.update_or_create(session, fkey=["playlist_id", "video_id"], **pl_vid)
                count += 1

        try:
            session.commit()
        except Exception:
            session.rollback()

        return BatchResponse(api_response=APIResponse(success=True,
                                                      data=result),
                             count=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch playlist items: {str(e)}")


@router.get("/info")
async def get_playlists_info(
    session: DBSessionDep,
    filters: Annotated[PlaylistFilter, Query()],
    ):
    
    """Return playlists stored in the database (up to 100 rows)."""
    
    try:
        rows = session.query(Playlist.__table__) \
                      .filter(and_(
                          Playlist.playlist_id.ilike(f"%{filters.playlist_id}%"),
                          Playlist.channel_id.ilike(f"%{filters.channel_id}%"),
                          Playlist.playlist_title.ilike(f"%{filters.playlist_title}%"),
                          Playlist.videos_count >= filters.min_number_of_videos,
                          Playlist.videos_count <= filters.max_number_of_videos,
                          Playlist.status.ilike(f"%{filters.status}%"),
                          Playlist.created_at > filters.date_range.start_date,
                          Playlist.created_at < filters.date_range.end_date
                          )).limit(filters.limit).all()

        result = [r._mapping for r in rows]
        
        return BatchResponse(
                api_response=APIResponse(success=True,
                                         data=result),
                count=len(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch playlists: {str(e)}")

@router.get("/items/info", response_model=BatchResponse)
async def get_playlist_items_info(
    session: DBSessionDep,
    playlist_id: str = "",
    video_id: str = "",
    limit: int = 100
    ):
    
    """Return playlist items stored in the database (up to 100 rows)."""
    rows = session.query(PlaylistsVideos.__table__) \
                  .filter(and_(PlaylistsVideos.playlist_id.like(f"%{playlist_id}%"),
                               PlaylistsVideos.video_id.like(f"%{video_id}%"))) \
                  .limit(limit).all()
    result = [r._mapping for r in rows]

    return BatchResponse(
        api_response=APIResponse(success=True,
                                 data=result),
        count=len(result))