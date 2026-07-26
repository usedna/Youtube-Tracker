"""
Channels API routes
"""
import logging

from fastapi import APIRouter, HTTPException
from api.v1.database import DBSessionDep
from api.v1.models.request import ChannelRequestById, ChannelRequestByHandle, BatchResponse, APIResponse
from api.v1.models.media_db import Channel
from api.v1.utils import service, unpack_channel_details


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/by-ids", response_model=BatchResponse)
async def get_channels_by_ids(
    request: ChannelRequestById,
    session: DBSessionDep,
) -> BatchResponse:
    """Get multiple channels by their IDs."""
    if not request.channel_ids:
        raise HTTPException(status_code=400, detail="channel_ids is required")

    try:
        result = service.get_channels_by_id(
            channel_ids=request.channel_ids,
            properties=request.properties,
            max_results=request.max_results
        )

        # Persist channels to DB (upsert)
        for item in result:
            details = unpack_channel_details(item)
            
            if not details:
                continue
            
            obj = Channel(**details)
            session.add(obj)

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Failed committing channels to DB")

        return BatchResponse(
            api_response=APIResponse(
                success=True,
                data=result
            ),
            count=len(result) if isinstance(result, list) else 1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch channels: {str(e)}")


@router.post("/by-handles", response_model=BatchResponse)
async def get_channels_by_handles(
    request: ChannelRequestByHandle,
    session: DBSessionDep,
) -> BatchResponse:
    """Get multiple channels by their handles/usernames."""
    if not request.channel_handles:
        raise HTTPException(status_code=400, detail="channel_handles is required")

    try:
        result = service.get_channels_by_handle(
            channel_handles=request.channel_handles,
            properties=request.properties,
            max_results=request.max_results
        )

        # Persist channels similar to /by-ids
        for item in result:
            details = unpack_channel_details(item)
            if not details:
                continue

            obj = Channel(**details)
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
        raise HTTPException(status_code=500, detail=f"Failed to fetch channels: {str(e)}")


@router.get("/info")
async def get_channels_info(
    session: DBSessionDep,
    limit: int = 100
    ):
    
    """Return channels stored in the database (up to 100 rows)."""
    rows = session.query(Channel).limit(limit).all()
    result = []
    for r in rows:
        result.append(r)

    return {"count": len(result), "channels": result}