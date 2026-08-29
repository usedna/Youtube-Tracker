from sqlalchemy import Column, String, Date, Boolean, Interval, ForeignKey, Integer, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from api.v1.database import Base
import datetime
import uuid

class Channel(Base):
    __tablename__ = "channels"
    
    channel_id = Column(String, primary_key=True, nullable=False)
    channel_handle = Column(String, unique=True, nullable=True)
    etag = Column(String, nullable=True)
    upload_id = Column(String, nullable=True)
    channel_name = Column(String, default="", unique=True, nullable=False)
    channel_description = Column(String, nullable=True)
    created_at = Column(Date, default="1970-01-01", nullable=False)
    country = Column(String(5), nullable=True)
    status = Column(String, nullable=True)
    made_for_kids = Column(Boolean, default=False, nullable=True)


class Video(Base):
    __tablename__ = "videos"

    video_id = Column(String, primary_key=True, nullable=False)
    channel_id = Column(String, ForeignKey("channels.channel_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    etag = Column(String, nullable=True)
    video_title = Column(String, default="", nullable=False)
    duration = Column(Interval, default=datetime.timedelta(0), nullable=False)
    video_description = Column(String, nullable=True)
    language = Column(String(5), nullable=True)
    tags = Column(String, nullable=True)
    dimension = Column(String(5), nullable=True)
    definition = Column(String, nullable=True)
    paid = Column(Boolean, default=False, nullable=False)
    captions = Column(Boolean, default=False, nullable=False)
    uploaded_at = Column(Date, default="1970-01-01", nullable=False)


class Playlist(Base):
    __tablename__ = "playlists"

    playlist_id = Column(String, primary_key=True, nullable=False)
    channel_id = Column(String, ForeignKey("channels.channel_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    playlist_title = Column(String, default="", nullable=False)
    description = Column(String, nullable=True)
    videos_count = Column(Integer, default=0, nullable=False)
    created_at = Column(Date, default="1970-01-01", nullable=False)
    status = Column(String, nullable=True)


class PlaylistsVideos(Base):
    __tablename__ = "playlists_videos"

    playlist_id = Column(String, ForeignKey("playlists.playlist_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    video_id = Column(String, ForeignKey("videos.video_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    position = Column(BigInteger, nullable=False)
    published_at = Column(Date, default="1970-01-01", nullable=True)


class Topic(Base):
    __tablename__ = "topics"

    topic_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    topic_name = Column(String, unique=True, nullable=False)
    topic_url = Column(String, unique=True, nullable=True)


class ChannelsTopics(Base):
    __tablename__ = "channels_topics"

    channel_id = Column(String, ForeignKey("channels.channel_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True, nullable=False)
    topics_id = Column(UUID(as_uuid=True), ForeignKey("topics.topic_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True, nullable=False)

