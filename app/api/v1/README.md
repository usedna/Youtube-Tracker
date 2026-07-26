# YouTube Data API v0.0.1

A FastAPI-based REST API for fetching YouTube data using the YouTube Data API v3.

## Features

- **Channels**: Fetch channel information by ID or handle
- **Playlists**: Retrieve playlists for specific channels
- **Videos**: Get video details by video IDs
- **Batch Operations**: Handle multiple IDs in single requests
- **Pagination Support**: Fetch all pages of results when needed

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export YOUTUBE_API_KEY="your_api_key_here"
# Optional: export YOUTUBE_AUTH_FILE="path/to/auth/file.json"
```

## Running the API

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Channels

- `POST /api/v1/channels/by-ids` - Get channels by IDs
- `POST /api/v1/channels/by-handles` - Get channels by handles
- `GET /api/v1/channels/info` - Get endpoint information

### Playlists

- `POST /api/v1/playlists/by-channel-ids` - Get playlists by channel IDs
- `GET /api/v1/playlists/info` - Get endpoint information

### Videos

- `POST /api/v1/videos/by-ids` - Get videos by IDs
- `GET /api/v1/videos/info` - Get endpoint information

## Documentation

- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Example Usage

```python
import requests

# Get channels by IDs
response = requests.post("http://localhost:8000/api/v1/channels/by-ids", json={
    "channel_ids": ["UC1234567890", "UC0987654321"],
    "properties": ["id", "snippet", "statistics"],
    "max_results": 50
})
```

## Configuration

The API can be configured using environment variables:

- `YOUTUBE_API_KEY`: Your YouTube Data API v3 key
- `YOUTUBE_AUTH_FILE`: Path to OAuth 2.0 credentials file (optional)
- `DEBUG`: Enable debug mode (default: false)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)