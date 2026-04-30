from api_client.service import youtube_parser as parser
from api_client.service.youtube_client import YoutubeAPIClient
from api_client.models.base import BaseParameters
from api_client.models import parameters
from api_client.utils import create_client, get_logger
from api_client.erros import handle_error
from typing import Iterable


class YoutubeDataService:    
    _DEFAULT_CHANNEL_PROPERTIES = (
        "id,snippet,statistics,topicDetails,contentDetails,"
        "brandingSettings,status,contentOwnerDetails,localizations")

    _DEFAULT_PLAYLIST_PROPERTIES = (
        "id,snippet,contentDetails,localizations,player,status"
    )

    _DEFAULT_PLAYLIST_ITEM_PROPERTIES = "id,snippet,contentDetails,status"

    _DEFAULT_VIDEO_PROPERTIES = (
        "contentDetails,id,liveStreamingDetails,localizations,"
        "paidProductPlacementDetails,player,recordingDetails,snippet,"
        "statistics,status,topicDetails"
    )

    def __init__(self, 
                 api_client: YoutubeAPIClient):

        self._api_client = api_client
        self._logger = get_logger(__name__)

    @classmethod
    def create_service(cls, api_key: str|None = None,
                       auth_file: str|None = None, 
                       scopes: list = []):
        
        client = create_client(api_key=api_key, secret_file=auth_file, scopes=scopes)
        api_client = YoutubeAPIClient(client)
        service = cls(api_client)
        return service
    
    @property
    def client(self) -> YoutubeAPIClient:
        return self._api_client

    def get_properties(self, properties_details: Iterable[str] | str | None, default: Iterable[str]) -> str:
        if not properties_details:
            return str(default)

        if isinstance(properties_details, Iterable) and not isinstance(properties_details, str):
            return ",".join(properties_details)

        return properties_details

    def _check_api_reponse(self, api_response: dict) -> None:
        if "error" in api_response:
            handle_error(api_response["error"], 
                         context=api_response["context"], 
                         logger=self._logger)

        if "items" not in api_response or not len(api_response["items"]):
            raise ValueError("API response is missing 'items' or it is empty")
        
    def _fetch_object(self,
                      parameters: BaseParameters,
                      api_fn: callable,
                      default_properties: Iterable[str],
                      parser_fn: callable,
                      type_name: str,
                      **kwargs) -> dict[str, any]:
        resp = {}
        
        try:
            parameters.properties_details = self.get_properties(parameters.properties_details, 
                                                                default_properties)
            
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
        
        return self._fetch_object(parameters,
                                  self.client.get_channels,
                                  self._DEFAULT_CHANNEL_PROPERTIES,
                                  parser.parse_channel_info,
                                  "channel",
                                  **kwargs)
        
    def get_playlists(self, parameters: parameters.PlaylistParameters, **kwargs) -> dict[str, any]:
        
        return self._fetch_object(parameters,
                                  self.client.get_playlists,
                                  self._DEFAULT_PLAYLIST_PROPERTIES,
                                  parser.parse_playlists_info,
                                  "playlist",
                                  **kwargs)
        

    def get_playlist_items(self, parameters: parameters.PlaylistItemParameters, **kwargs) -> dict[str, any]:
        
        return self._fetch_object(parameters,
                                  self.client.get_playlist_items,
                                  self._DEFAULT_PLAYLIST_ITEM_PROPERTIES,
                                  parser.parse_playlist_items_info,
                                  "playlist item",
                                  **kwargs)
            
    def get_videos(self, parameters: parameters.VideoParameters, **kwargs) -> dict[str, any]:
        
        return self._fetch_object(parameters,
                                  self.client.get_videos,
                                  self._DEFAULT_VIDEO_PROPERTIES,
                                  parser.parse_videos_info,
                                  "video",
                                  **kwargs)

    def get_max_results(self, max_results: int, ids_count: int = 0) -> int:
        if max_results > 50 or ids_count >= 50:
            return 50
        elif ids_count > max_results:
            return ids_count
        
        return max_results
    
    def chunk_ids(self, ids: list[str], ids_count: int = 0, size: int = 50) -> Iterable[list[str]]:
        if ids_count == 0:
            ids_count = len(ids)
        
        for i in range(0, ids_count, size):
            yield ids[i:i+size]
            
    def _batched_execute(self, param: BaseParameters, api_fn: callable, **kwargs) -> list[dict]:
        ids_count = len(param.id)

        param.max_results = self.get_max_results(param.max_results, ids_count)
        
        results = []
        for batch in self.chunk_ids(param.id, ids_count, param.max_results):
            param.id = batch
            result = api_fn(param, **kwargs)
            results.extend(result)
        return results

    def _pagination_execute(self, first_output: dict, param: BaseParameters, api_fn: callable, fetch_all: bool = False, **kwargs) -> list[dict]:
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
        if pagination:
            param.max_results = 50
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

        params = parameters.ChannelParameters(id=channel_ids,
                                              properties_details=properties,
                                              max_results=max_results)

        return self._batched_execute(params, self.get_channel_details, **kwargs)

    def get_channels_by_handle(self,
                               channel_handles: list[str],
                               properties: list[str]|str|None = None,
                               max_results: int = 50,
                               **kwargs) -> list[dict]:
        params = parameters.ChannelParameters(properties_details=properties,
                                                 max_results=max_results)
        
        return self._incremental_execute("channel_handle", channel_handles, params, self.get_channel_details, **kwargs)
    
    def get_playlists_by_channel_id(self,
                                    channel_ids: str,
                                    properties: list[str]|str|None = None,
                                    max_results: int = 50,
                                    fetch_all: bool = False,
                                    **kwargs) -> list[dict]:
        
        params = parameters.PlaylistParameters(properties_details=properties,
                                                  max_results=max_results)
        
        return self._incremental_execute("channel_id", channel_ids, params, self.get_playlists, pagination=True, fetch_all=fetch_all, **kwargs)

    def get_playlist_items_by_id(self,
                                 item_ids: list[str],
                                 properties: list[str]|str|None = None,
                                 max_results: int = 50,
                                 **kwargs) -> list[dict]:

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

        params = parameters.PlaylistItemParameters(properties_details=properties,
                                                   max_results=max_results)

        return self._incremental_execute("playlist_id", playlist_ids, params, self.get_playlist_items, pagination=True, fetch_all=fetch_all, **kwargs)

    def get_videos_by_id(self,
                         video_ids: list[str],
                         properties: list[str]|str|None = None,
                         max_results: int = 50,
                         **kwargs) -> list[dict]:

        params = parameters.VideoParameters(id=video_ids,
                                               properties_details=properties,
                                               max_results=max_results,
                                               **kwargs)

        return self._batched_execute(params, self.get_videos)