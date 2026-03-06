from api_client.youtube_parser import YoutubeAPIDataParser
from api_client.youtube_client import YoutubeAPIClient
from api_client.models.parameters import ChannelParameters, PlaylistParameters, PlaylistItemParameters, VideoParameters
from api_client.utils import create_client
from api_client.utils import get_logger
from api_client.erros import handle_error
from typing import Literal, Iterable
from common.settings import YT_API_KEY, scopes


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
                 api_client: YoutubeAPIClient, 
                 data_parser: YoutubeAPIDataParser):

        self._api_client = api_client
        self._data_parser = data_parser
        self._logger = get_logger(__name__)

    @property        
    def client(self) -> YoutubeAPIClient:
        return self._api_client

    @property
    def parser(self) -> YoutubeAPIDataParser:
        return self._data_parser

    def get_properties(self, properties_details: Iterable[str] | str | None, default: Literal[str]) -> str:
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

    def get_channel_details(self, parameters: ChannelParameters , **kwargs) -> dict[str, any]:
        resp = {}
        
        try:
            parameters.properties_details = self.get_properties(parameters.properties_details, 
                                                                self._DEFAULT_CHANNEL_PROPERTIES)
            
            api_response = self.client.get_channels(parameters=parameters,
                                                         **kwargs)
            self._check_api_reponse(api_response)

            resp = self.parser.parse_channel_info(api_response)
            
        except Exception as err:
            print(f"Failed to fetch requested channels from API: {err=}, {type(err)=}")
            self._logger.debug(f"Failed to fetch requested channels from API: {err=}, {type(err)=}")

        finally:
            return resp

    def get_playlists(self, parameters: PlaylistParameters, **kwargs):
        resp = {}
        
        try:
            parameters.properties_details = self.get_properties(parameters.properties_details, 
                                                                self._DEFAULT_PLAYLIST_PROPERTIES)
            
            api_response = self.client.get_playlists(parameters=parameters,
                                                          **kwargs)
            
            self._check_api_reponse(api_response)
            
            resp = self.parser.parse_playlists_info(api_response)
        
        except Exception as err:
            resp = {"error": type(err),
                    "msg": f"Failed to fetch requested playlists from API"}
            print(f"Failed to fetch requested playlists from API: {err=}, {type(err)=}")
            self._logger.debug(f"Failed to fetch requested playlists from API: {err=}, {type(err)=}")
        
        finally:
            return resp
            
    def get_playlist_items(self, parameters: PlaylistItemParameters, **kwargs):
        resp = {}
        
        try:
            parameters.properties_details = self.get_properties(parameters.properties_details, 
                                                                self._DEFAULT_PLAYLIST_ITEM_PROPERTIES)

            api_response = self.client.get_playlist_items(parameters=parameters,
                                                               **kwargs)

            self._check_api_reponse(api_response)

            resp = self.parser.parse_playlist_items_info(api_response)
        
        except Exception as err:
            print(f"Failed to fetch requested playlist items from API: {err=}, {type(err)=}")
            self._logger.debug(f"Failed to fetch requested playlist items from API: {err=}, {type(err)=}")
                    
        finally:
            return resp
            
    def get_videos(self, parameters: VideoParameters, **kwargs) -> dict:
        resp = {}
        
        try:
            parameters.properties_details = self.get_properties(parameters.properties_details, 
                                                                self._DEFAULT_VIDEO_PROPERTIES)
            
            api_response = self.client.get_videos(parameters=parameters,
                                                       **kwargs)

            self._check_api_reponse(api_response)

            resp = self.parser.parse_videos_info(api_response)

        except Exception as err:

            print(f"Failed to fetch requested videos from API: {err=}, {type(err)=}")
            self._logger.debug(f"Failed to fetch requested videos from API: {err=}, {type(err)=}")
            
        finally:
            return resp


def get_youtube_service():
    client = create_client(api_key=YT_API_KEY, scopes=scopes)
    parser = YoutubeAPIDataParser()
    api_client = YoutubeAPIClient(client)
    service = YoutubeDataService(api_client, parser)
    return service
