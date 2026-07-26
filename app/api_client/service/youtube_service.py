from app.api_client.service import youtube_parser as parser
from app.api_client.service.youtube_client import YoutubeAPIClient
from app.api_client.models.base import BaseParameters
from app.api_client.models import parameters
from app.api_client.utils import create_client, get_logger
from app.api_client.erros import handle_error
from typing import Iterable


class YoutubeDataService:
    # Default properties organized by resource type
    _DEFAULT_PROPERTIES = {
        "channel": (
            "id,snippet,statistics,topicDetails,contentDetails,"
            "brandingSettings,status,contentOwnerDetails,localizations"
        ),
        "playlist": (
            "id,snippet,contentDetails,localizations,player,status"
        ),
        "playlist_item": "id,snippet,contentDetails,status",
        "video": (
            "contentDetails,id,liveStreamingDetails,localizations,"
            "paidProductPlacementDetails,player,recordingDetails,snippet,"
            "statistics,status,topicDetails"
        )
    }

    # YouTube API constraints
    MAX_RESULTS_PER_REQUEST = 50
    MAX_IDS_PER_REQUEST = 50

    def __init__(self, 
                 api_client: YoutubeAPIClient):
        """Initialize YoutubeDataService with an API client.
        
        Args:
            api_client: An instance of YoutubeAPIClient for making API requests.
        """
        self._api_client = api_client
        self._logger = get_logger(__name__)

    @classmethod
    def create_service(cls, api_key: str|None = None,
                       auth_file: str|None = None, 
                       scopes: list = []):
        """Factory method to create a YoutubeDataService instance.
        
        Args:
            api_key: Optional API key for YouTube Data API authentication.
            auth_file: Optional path to authentication file for OAuth 2.0.
            scopes: Optional list of OAuth scopes required for authentication.
            
        Returns:
            An initialized YoutubeDataService instance.
        """
        client = create_client(api_key=api_key, secret_file=auth_file, scopes=scopes)
        api_client = YoutubeAPIClient(client)
        service = cls(api_client)
        return service
    
    @property
    def client(self) -> YoutubeAPIClient:
        """Get the underlying YoutubeAPIClient instance.
        
        Returns:
            The YoutubeAPIClient used for making API requests.
        """
        return self._api_client

    def get_properties(self, properties_details: Iterable[str] | str | None, type_name: str) -> str:
        """Convert properties to comma-separated string format.
        
        Args:
            properties_details: Properties as a list, string, or None.
            type_name: Name of the resource type for default properties lookup.
            
        Returns:
            Comma-separated string of properties.
        """
        if not properties_details:
            return str(self._DEFAULT_PROPERTIES.get(type_name, ""))
        
        if isinstance(properties_details, Iterable) and not isinstance(properties_details, str):
            prop = ",".join(properties_details)
            if not prop.strip():
                return str(self._DEFAULT_PROPERTIES.get(type_name, ""))
            return prop
        
        elif isinstance(properties_details, str):
            if not properties_details.strip():
                return str(self._DEFAULT_PROPERTIES.get(type_name, ""))

        return properties_details

    def _check_api_reponse(self, api_response: dict) -> None:
        """Validate API response for errors and required fields.
        
        Args:
            api_response: The response dictionary from the API.
            
        Raises:
            Exception: If the response contains an error (handled via handle_error).
            ValueError: If 'items' field is missing or empty in the response.
        """
        if "error" in api_response:
            handle_error(api_response["error"], 
                         context=api_response["context"], 
                         logger=self._logger)

        if "items" not in api_response or not len(api_response["items"]):
            raise ValueError("API response is missing 'items' or it is empty")
        
    def _fetch_object(self,
                      parameters: BaseParameters,
                      api_fn: callable,
                      parser_fn: callable,
                      type_name: str,
                      **kwargs) -> dict[str, any]:
        """Fetch a single object from the YouTube API with error handling.
        
        Args:
            parameters: The request parameters object.
            api_fn: The API client method to call for fetching data.
            default_properties: Default properties to fetch if none specified.
            parser_fn: Function to parse the API response.
            type_name: Name of the object type (for logging).
            **kwargs: Additional keyword arguments to pass to api_fn.
            
        Returns:
            Dictionary containing parsed data or error information.
        """
        resp = {}
        
        try:
            parameters.properties_details = self.get_properties(parameters.properties_details, 
                                                                type_name)
            
            api_response = api_fn(parameters=parameters, **kwargs)
            self._check_api_reponse(api_response)
            resp = parser_fn(api_response)

            self._logger.debug(f"Successfully fetched {type_name} details from API: {resp=}")
            
        except Exception as err:
            resp = {"error": type(err),
                    "msg": f"Failed to fetch requested {type_name} from API"}
            print(f"Failed to fetch requested {type_name} from API: {err=}, {type(err)=}")
            self._logger.debug(f"Failed to fetch requested {type_name} from API: {err=}, {type(err)=}")
            
        finally:
            return resp

    def get_channel_details(self, parameters: parameters.ChannelParameters, **kwargs) -> dict[str, any]:
        """Fetch channel details from the YouTube API.
        
        Args:
            parameters: Channel request parameters including ID or handle.
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            Dictionary containing parsed channel details or error information.
        """
        return self._fetch_object(parameters,
                                  self.client.get_channels,
                                  parser.parse_channel_info,
                                  "channel",
                                  **kwargs)
        
    def get_playlists(self, parameters: parameters.PlaylistParameters, **kwargs) -> dict[str, any]:
        """Fetch playlist details from the YouTube API.
        
        Args:
            parameters: Playlist request parameters.
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            Dictionary containing parsed playlist details or error information.
        """
        return self._fetch_object(parameters,
                                  self.client.get_playlists,
                                  parser.parse_playlists_info,
                                  "playlist",
                                  **kwargs)
        

    def get_playlist_items(self, parameters: parameters.PlaylistItemParameters, **kwargs) -> dict[str, any]:
        """Fetch playlist item details from the YouTube API.
        
        Args:
            parameters: Playlist item request parameters.
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            Dictionary containing parsed playlist item details or error information.
        """
        return self._fetch_object(parameters,
                                  self.client.get_playlist_items,
                                  parser.parse_playlist_items_info,
                                  "playlist_item",
                                  **kwargs)
            
    def get_videos(self, parameters: parameters.VideoParameters, **kwargs) -> dict[str, any]:
        """Fetch video details from the YouTube API.
        
        Args:
            parameters: Video request parameters.
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            Dictionary containing parsed video details or error information.
        """
        return self._fetch_object(parameters,
                                  self.client.get_videos,
                                  parser.parse_videos_info,
                                  "video",
                                  **kwargs)

    def get_max_results(self, max_results: int, ids_count: int = 0) -> int:
        """Calculate appropriate max_results value for API calls.
        
        The YouTube API has a maximum limit of 50 items per request. This method
        ensures the max_results value doesn't exceed API constraints.
        
        Args:
            max_results: The requested maximum number of results.
            ids_count: The number of IDs to fetch (optional).
            
        Returns:
            The maximum number of results to request (max 50).
        """
        if max_results > self.MAX_RESULTS_PER_REQUEST or ids_count >= self.MAX_RESULTS_PER_REQUEST:
            return self.MAX_RESULTS_PER_REQUEST
        elif ids_count > max_results:
            return ids_count
        
        return max_results
    
    def chunk_ids(self, ids: list[str], ids_count: int = 0, size: int = 50) -> Iterable[list[str]]:
        """Split a list of IDs into chunks of specified size.
        
        Args:
            ids: List of IDs to chunk.
            ids_count: Number of IDs to process (if 0, uses length of ids).
            size: Size of each chunk (default 50).
            
        Yields:
            Chunks of IDs as lists.
        """
        if ids_count == 0:
            ids_count = len(ids)
        
        for i in range(0, ids_count, size):
            yield ids[i:i+size]
            
    def _batched_execute(self, param: BaseParameters, api_fn: callable, **kwargs) -> list[dict]:
        """Execute API calls in batches to handle large ID lists.
        
        The YouTube API allows up to 50 IDs per request. This method splits
        the ID list and makes multiple requests.
        
        Args:
            param: The request parameters containing IDs to process.
            api_fn: The API method to call for each batch.
            **kwargs: Additional arguments passed to api_fn.
            
        Returns:
            Combined list of results from all batches.
        """
        ids_count = len(param.id)

        param.max_results = self.get_max_results(param.max_results, ids_count)
        
        results = []
        for batch in self.chunk_ids(param.id, ids_count, param.max_results):
            param.id = batch
            result = api_fn(param, **kwargs)
            results.extend(result if isinstance(result, list) else [result])
        return results

    def _pagination_execute(self, first_output: dict, param: BaseParameters, api_fn: callable, fetch_all: bool = False, **kwargs) -> list[dict]:
        """Execute paginated API calls to retrieve all results.
        
        The YouTube API returns paginated results with a next_page_token.
        This method handles pagination to fetch all available results if requested.
        
        Args:
            first_output: The first API response containing items and next_page_token.
            param: The request parameters.
            api_fn: The API method to call for subsequent pages.
            fetch_all: Whether to fetch all pages (if False, returns first page only).
            **kwargs: Additional arguments passed to api_fn.
            
        Returns:
            Combined list of items from all pages (or first page only if fetch_all=False).
        """
        if not fetch_all:
            return [first_output]
        
        results = []
        item, _, next_page_token = first_output
        results.extend(item)

        while next_page_token:
            param.page_token = next_page_token
            items, _, next_page_token = api_fn(param, **kwargs)
            results.extend(items)
            
        
        return results
    
    def _incremental_execute(self, inc_param_name: str, inc_param_vals: list[str], param: BaseParameters, api_fn: callable, pagination: bool = False, fetch_all: bool = False, **kwargs):
        """Execute API calls incrementally over a list of parameter values.
        
        This method iterates through a list of values (e.g., channel IDs) and
        makes individual API calls for each value, optionally with pagination.
        
        Args:
            inc_param_name: Name of the parameter to iterate over (e.g., 'channel_id').
            inc_param_vals: List of values to iterate through.
            param: The base request parameters.
            api_fn: The API method to call for each value.
            pagination: Whether to enable pagination for each call.
            fetch_all: Whether to fetch all pages when pagination is enabled.
            **kwargs: Additional arguments passed to api_fn.
            
        Returns:
            Combined list of results from all incremental calls.
        """
        if pagination:
            param.max_results = self.MAX_RESULTS_PER_REQUEST
        else:
            param.max_results = self.get_max_results(param.max_results)
        
        results = []
        
        for val in inc_param_vals:
            setattr(param, inc_param_name, val)
            result = api_fn(param, **kwargs)
            
            if pagination:
                result = self._pagination_execute(result, param, api_fn, fetch_all, **kwargs)
            
            results.extend(result)
        return results


    def get_channels_by_id(self, 
                           channel_ids: list[str],
                           properties: list[str]|str|None = None,
                           max_results: int = 50,
                           **kwargs) -> list[dict]:
        """Fetch multiple channels by their IDs.
        
        Args:
            channel_ids: List of YouTube channel IDs to fetch.
            properties: Specific properties to retrieve for each channel.
            max_results: Maximum results per request (max 50, default 50).
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            List of dictionaries containing channel details.
        """
        params = parameters.ChannelParameters(id=channel_ids,
                                              properties_details=properties,
                                              max_results=max_results)

        return self._batched_execute(params, self.get_channel_details, **kwargs)

    def get_channels_by_handle(self,
                               channel_handles: list[str],
                               properties: list[str]|str|None = None,
                               max_results: int = 50,
                               **kwargs) -> list[dict]:
        """Fetch multiple channels by their handles/usernames.
        
        Args:
            channel_handles: List of YouTube channel handles to fetch.
            properties: Specific properties to retrieve for each channel.
            max_results: Maximum results per request (max 50, default 50).
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            List of dictionaries containing channel details.
        """
        params = parameters.ChannelParameters(properties_details=properties,
                                              max_results=max_results)
        
        return self._incremental_execute("channel_handle", channel_handles, params, self.get_channel_details, **kwargs)
    
    def get_playlists_by_channel_id(self,
                                    channel_ids: str,
                                    properties: list[str]|str|None = None,
                                    max_results: int = 50,
                                    fetch_all: bool = False,
                                    **kwargs) -> list[dict]:
        """Fetch all playlists for one or more channels.
        
        Args:
            channel_ids: List of YouTube channel IDs to fetch playlists from.
            properties: Specific properties to retrieve for each playlist.
            max_results: Maximum results per request (max 50, default 50).
            fetch_all: Whether to fetch all pages of playlists (if True, ignores max_results).
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            List of dictionaries containing playlist details.
        """
        params = parameters.PlaylistParameters(properties_details=properties,
                                               max_results=max_results)
        
        return self._incremental_execute("channel_id", channel_ids, params, self.get_playlists, pagination=True, fetch_all=fetch_all, **kwargs)
    
    def get_playlists_by_playlist_id(self,
                                     playlist_ids: list[str],
                                     properties: list[str]|str|None = None,
                                     max_results: int = 50,
                                     **kwargs) -> list[dict]:
        """Fetch all playlists by their IDs.
        
        Args:
            playlist_ids: List of YouTube playlist IDs to fetch.
            properties: Specific properties to retrieve for each playlist.
            max_results: Maximum results per request (max 50, default 50).
            fetch_all: Whether to fetch all pages of playlists (if True, ignores max_results).
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            List of dictionaries containing playlist details.
        """
        params = parameters.PlaylistParameters(id=playlist_ids,
                                               properties_details=properties,
                                               max_results=max_results)
        
        return self._batched_execute(params, self.get_playlists, **kwargs)

    def get_playlist_items_by_id(self,
                                 item_ids: list[str],
                                 properties: list[str]|str|None = None,
                                 max_results: int = 50,
                                 **kwargs) -> list[dict]:
        """Fetch multiple playlist items by their IDs.
        
        Args:
            item_ids: List of YouTube playlist item IDs to fetch.
            properties: Specific properties to retrieve for each item.
            max_results: Maximum results per request (max 50, default 50).
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            List of dictionaries containing playlist item details.
        """
        params = parameters.PlaylistItemParameters(id=item_ids,
                                                   properties_details=properties,
                                                   max_results=max_results)

        return self._batched_execute(params, self.get_playlist_items, **kwargs)

    def get_playlist_items_by_playlist_id(self,
                                          playlist_ids: list[str],
                                          properties: list[str]|str|None = None,
                                          max_results: int = 50,
                                          fetch_all: bool = False,
                                          **kwargs) -> list[dict]:
        """Fetch all items from one or more playlists.
        
        Args:
            playlist_ids: List of YouTube playlist IDs to fetch items from.
            properties: Specific properties to retrieve for each item.
            max_results: Maximum results per request (max 50, default 50).
            fetch_all: Whether to fetch all pages of items (if True, ignores max_results).
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            List of dictionaries containing playlist item details.
        """
        params = parameters.PlaylistItemParameters(properties_details=properties,
                                                   max_results=max_results)

        return self._incremental_execute("playlist_id", playlist_ids, params, 
                                         self.get_playlist_items, pagination=True, 
                                         fetch_all=fetch_all, **kwargs)

    def get_videos_by_id(self,
                         video_ids: list[str],
                         properties: list[str]|str|None = None,
                         max_results: int = 50,
                         **kwargs) -> list[dict]:
        """Fetch multiple videos by their IDs.
        
        Args:
            video_ids: List of YouTube video IDs to fetch.
            properties: Specific properties to retrieve for each video.
            max_results: Maximum results per request (max 50, default 50).
            **kwargs: Additional arguments passed to the API client.
            
        Returns:
            List of dictionaries containing video details.
        """
        params = parameters.VideoParameters(id=video_ids,
                                               properties_details=properties,
                                               max_results=max_results,
                                               **kwargs)

        return self._batched_execute(params, self.get_videos)