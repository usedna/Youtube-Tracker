"""
FastAPI application for YouTube Data API v0.0.1
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.v1.database import init_db
import logging

from api.v1.routes import channels, playlists, videos

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


origins = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Starting YouTube API v0.0.1")
    init_db()
    yield
    logger.info("Shutting down YouTube API v0.0.1")

# Create FastAPI app
app = FastAPI(
    title="YouTube Data API",
    description="REST API for fetching YouTube data using YouTube Data API v3",
    version="0.0.1",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    channels.router,
    prefix="/api/v1/channels",
    tags=["channels"]
)

app.include_router(
    playlists.router,
    prefix="/api/v1/playlists",
    tags=["playlists"]
)

app.include_router(
    videos.router,
    prefix="/api/v1/videos",
    tags=["videos"]
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "YouTube Data API v0.0.1",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.0.1"}