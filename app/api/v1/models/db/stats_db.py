"""Statistics models for videos and channels.

This file defines `videos_stats` and `channel_stats` tables used for storing
periodic metrics. Uses PostgreSQL UUID primary keys.
"""
from datetime import date
import uuid

from sqlalchemy import Column, String, Date, BigInteger, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.api.v1.models.media_db import Base


class VideosStats(Base):
    __tablename__ = "videos_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    video_id = Column(String, ForeignKey("videos.video_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    video_views = Column(BigInteger, nullable=False, default=0)
    video_likes = Column(BigInteger, nullable=False, default=0)
    comments_count = Column(Integer, nullable=False, default=0)


class ChannelStats(Base):
    __tablename__ = "channel_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    channel_id = Column(String, ForeignKey("channels.channel_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    total_views = Column(BigInteger, nullable=False, default=0)
    subscribers = Column(BigInteger, nullable=False, default=0)
