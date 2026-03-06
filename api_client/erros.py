from googleapiclient.errors import HttpError
from google.auth.exceptions import GoogleAuthError
from api_client.utils import get_logger

class YoutubeAPIError(Exception):
    """Base exception for YouTube API errors."""
    pass


class YoutubeAPIAuthError(YoutubeAPIError):
    """Exception raised for authentication failures."""
    pass


class YoutubeAPIHttpError(YoutubeAPIError):
    """Exception raised for HTTP errors from YouTube API."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
        
def handle_error(error: Exception, context: str = "", logger=None) -> None:
        """
        Centralized error handling with proper logging and classification.
        
        Args:
            error: The exception that was caught
            context: Description of where the error occurred
        """
        
        if logger is None:
            logger = get_logger(__name__)
        
        if isinstance(error, HttpError):
                        
            # Handle YouTube API HTTP errors specifically
            status_code = error.resp.status
            error_msg = f"YouTube API HTTP error {status_code}: {error.error_details}"
            
            if status_code == 401 or status_code == 403:
                logger.error(f"Authentication/Authorization error in {context}: {error_msg}")
                raise YoutubeAPIAuthError(f"Authentication failed: {error_msg}")
            
            else:
                logger.error(f"HTTP error in {context}: {error_msg}")
                raise YoutubeAPIHttpError(error_msg, status_code)
                
        elif isinstance(error, GoogleAuthError):
            logger.error(f"Google Auth error in {context}: {error}")
            raise YoutubeAPIAuthError(f"Authentication error: {error}")
            
        elif isinstance(error, (ValueError, TypeError)):
            logger.error(f"Validation error in {context}: {error}")
            raise YoutubeAPIError(f"Invalid request: {error}")

        else:
            logger.exception(f"Unexpected error in {context}: {error}")
            raise YoutubeAPIError(f"An unexpected error occurred: {error}")
