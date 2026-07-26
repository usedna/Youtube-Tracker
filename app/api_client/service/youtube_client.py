import app.api_client.utils as utils
from app.api_client.models.parameters import ChannelParameters, PlaylistParameters, PlaylistItemParameters, VideoParameters
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from typing import Dict, Any, Optional
import time


class YoutubeAPIClient:
    """YouTube Data API v3 client wrapper with error handling and logging."""

    # API operation constants
    DEFAULT_OPERATION = "list"

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds

    def __init__(self, client: Resource):
        """Initialize the YouTube API client.

        Args:
            client: Google API client resource for YouTube Data API v3.

        Raises:
            ValueError: If client is None or invalid.
        """
        if client is None:
            raise ValueError("YouTube API client cannot be None")

        self._client = client
        self._logger = utils.get_logger(__name__)
    
    def _fetch_data(self, obj_name: str, obj_type: str = "", op_type: str = DEFAULT_OPERATION, save_to_file: bool = False, **kwargs) -> Dict[str, Any]:
        """Execute a YouTube Data API request and handle responses with retry logic.

        This is a generic method that handles API calls to different YouTube endpoints.
        It includes error handling, retry logic for transient failures, and optional
        response saving to JSON files.

        Args:
            obj_name: Name of the object being fetched (e.g., 'channels', 'videos').
            obj_type: API resource type (defaults to obj_name if empty).
            op_type: API operation type (default 'list').
            save_to_file: Whether to save the response to a JSON file.
            **kwargs: Additional parameters to pass to the API request.

        Returns:
            Dictionary containing the API response or error information.
        """
        if not obj_type.strip():
            obj_type = obj_name

        # Validate required parameters
        if not obj_name:
            return {"error": ValueError("obj_name cannot be empty"), "context": "validation"}

        for attempt in range(self.MAX_RETRIES):
            try:
                # Get the API resource and operation
                api_resource = getattr(self._client, obj_type)()
                api_method = getattr(api_resource, op_type)

                # Execute the request
                request = api_method(**kwargs)
                response = request.execute()

                # Save response if requested
                if save_to_file:
                    utils.save_json(response, f"{obj_name}_{op_type}_response.json")

                self._logger.debug(f"Successfully fetched {obj_name} data")
                return response

            except HttpError as http_err:
                error_details = self._handle_http_error(http_err, obj_name, op_type, attempt)
                if error_details.get("retry", False):
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                return error_details

            except Exception as err:
                error_msg = f"Unexpected error fetching {obj_name} data: {err}"
                self._logger.error(error_msg)
                print(error_msg)
                return {"error": err, "context": f"{obj_name}_{op_type}"}

        # If all retries exhausted
        return {"error": "Max retries exceeded", "context": f"{obj_name}_{op_type}"}

    def _handle_http_error(self, http_err: HttpError, obj_name: str, op_type: str, attempt: int) -> Dict[str, Any]:
        """Handle HTTP errors from YouTube API with appropriate retry logic.

        Args:
            http_err: The HttpError exception from Google API client.
            obj_name: Name of the object being fetched.
            op_type: API operation type.
            attempt: Current retry attempt number.

        Returns:
            Dictionary containing error information and retry flag.
        """
        status_code = http_err.resp.status
        error_details = http_err.error_details if hasattr(http_err, 'error_details') else {}

        context = f"{obj_name}_{op_type}"
        error_info = {
            "error": http_err,
            "context": context,
            "status_code": status_code,
            "error_details": error_details
        }

        # Handle different error types
        if status_code == 403:
            # Quota exceeded or forbidden
            error_msg = f"YouTube API quota exceeded or access forbidden for {obj_name}"
            self._logger.warning(error_msg)
            error_info["retry"] = False

        elif status_code == 404:
            # Resource not found
            error_msg = f"Resource not found for {obj_name}"
            self._logger.warning(error_msg)
            error_info["retry"] = False

        elif status_code >= 500:
            # Server errors - retry
            error_msg = f"YouTube API server error ({status_code}) for {obj_name}, attempt {attempt + 1}"
            self._logger.warning(error_msg)
            error_info["retry"] = attempt < self.MAX_RETRIES - 1

        elif status_code == 429:
            # Too many requests - retry with longer delay
            error_msg = f"YouTube API rate limit exceeded for {obj_name}, attempt {attempt + 1}"
            self._logger.warning(error_msg)
            error_info["retry"] = attempt < self.MAX_RETRIES - 1

        else:
            # Other client errors - don't retry
            error_msg = f"YouTube API error ({status_code}) for {obj_name}"
            self._logger.error(error_msg)
            error_info["retry"] = False

        print(error_msg)
        return error_info
    
    def get_channels(self,
                     parameters: ChannelParameters,
                    **kwargs) -> Dict[str, Any]:
        """Fetch channel data from the YouTube Data API.

        Args:
            parameters: ChannelParameters object containing request parameters
                including channel IDs, handles, and properties to fetch.
            **kwargs: Additional keyword arguments for the API request
                (e.g., pageToken for pagination).

        Returns:
            Dictionary containing channel data or error information.
            Successful response includes 'items' array with channel details.
        """
        return self._fetch_data(obj_name="channels",
                                op_type=self.DEFAULT_OPERATION,
                                id=parameters.id,
                                forHandle=parameters.channel_handle,
                                part=parameters.properties_details,
                                maxResults=parameters.max_results,
                                **kwargs)

    def get_playlists(self,
                      parameters: PlaylistParameters,
                      **kwargs) -> Dict[str, Any]:
        """Fetch playlist data from the YouTube Data API.

        Args:
            parameters: PlaylistParameters object containing request parameters
                including channel ID, playlist IDs, and properties to fetch.
            **kwargs: Additional keyword arguments for the API request
                (e.g., pageToken for pagination).

        Returns:
            Dictionary containing playlist data or error information.
            Successful response includes 'items' array with playlist details.
        """
        return self._fetch_data(obj_name="playlists",
                                op_type=self.DEFAULT_OPERATION,
                                channelId=parameters.channel_id,
                                id=parameters.id,
                                part=parameters.properties_details,
                                maxResults=parameters.max_results,
                                **kwargs)

    def get_playlist_items(self,
                           parameters: PlaylistItemParameters,
                           **kwargs) -> Dict[str, Any]:
        """Fetch playlist item data from the YouTube Data API.

        Args:
            parameters: PlaylistItemParameters object containing request parameters
                including playlist ID, item IDs, and properties to fetch.
            **kwargs: Additional keyword arguments for the API request
                (e.g., pageToken for pagination).

        Returns:
            Dictionary containing playlist item data or error information.
            Successful response includes 'items' array with playlist item details.
        """
        return self._fetch_data(obj_name="playlist_items",
                                obj_type="playlistItems",
                                op_type=self.DEFAULT_OPERATION,
                                playlistId=parameters.playlist_id,
                                id=parameters.id,
                                part=parameters.properties_details,
                                maxResults=parameters.max_results,
                                **kwargs)

    def get_videos(self,
                   parameters: VideoParameters,
                   **kwargs) -> Dict[str, Any]:
        """Fetch video data from the YouTube Data API.

        Args:
            parameters: VideoParameters object containing request parameters
                including video IDs and properties to fetch.
            **kwargs: Additional keyword arguments for the API request
                (e.g., pageToken for pagination, though videos endpoint
                typically doesn't support pagination).

        Returns:
            Dictionary containing video data or error information.
            Successful response includes 'items' array with video details.
        """
        return self._fetch_data(obj_name="videos",
                                op_type=self.DEFAULT_OPERATION,
                                id=parameters.id,
                                part=parameters.properties_details,
                                maxResults=parameters.max_results,
                                **kwargs)

    def is_initialized(self) -> bool:
        """Check if the YouTube API client is properly initialized.

        Returns:
            True if the client is ready to make API calls, False otherwise.
        """
        return self._client is not None

    def get_quota_info(self) -> Optional[Dict[str, Any]]:
        """Get current API quota information if available.

        Returns:
            Dictionary with quota information or None if not available.
            Note: This is a placeholder for future quota tracking implementation.
        """
        # This could be extended to track API usage
        # For now, return None as quota info isn't directly available
        return None