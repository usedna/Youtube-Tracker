import api_client.utils as utils
from api_client.models.parameters import ChannelParameters, PlaylistParameters, PlaylistItemParameters, VideoParameters
from googleapiclient.discovery import Resource


def save_response_to_file(response: dict[str, any], filename: str):
    import json
    with open(filename, "w") as f:
        json.dump(response, f, indent=4)

class YoutubeAPIClient:
    def __init__(self, client: Resource):
        
        self._client = client
        self._logger = utils.get_logger(__name__)
    
    def _fetch_data(self, obj_name: str, obj_type: str = "", op_type: str = "list", save_to_file: bool = False, **kwargs) -> dict[str, any]:
        try:
            if not obj_type.strip():
                obj_type = f"{obj_name}"
            
            func = getattr(self._client, obj_type)()
            request = getattr(func, op_type)(**kwargs)
            response = request.execute()
            
            if save_to_file:
                save_response_to_file(response, f"{obj_name}_{op_type}_response.json")

        except Exception as err:
            response = {"error": err,
                        "context": f"{obj_name}_{op_type}",}
            print(f"Failed to fetch {obj_name} data: {err}, {type(err)}")
            self._logger.debug(f"Failed to fetch {obj_name} data: {err}, {type(err)}")
        
        finally:
            return response
    
    def get_channels(self,
                     parameters: ChannelParameters,
                    **kwargs) -> dict[str, any]:
        
        return self._fetch_data(obj_name="channels", 
                                op_type="list",  
                                id=parameters.id,
                                forHandle=parameters.channel_handle,
                                part=parameters.properties_details,
                                maxResults=parameters.max_results,
                                **kwargs)

    def get_playlists(self,
                      parameters: PlaylistParameters,
                      **kwargs) -> dict[str, any]:
        
        return self._fetch_data(obj_name="playlists",
                                op_type="list",
                                channelId=parameters.channel_id,
                                id=parameters.id,
                                part=parameters.properties_details,
                                maxResults=parameters.max_results,
                                **kwargs)

    def get_playlist_items(self,
                           parameters: PlaylistItemParameters,
                           **kwargs) -> dict | None:
        
        return self._fetch_data(obj_name="playlist_items",
                                obj_type="playlistItems",
                                op_type="list",
                                playlistId=parameters.playlist_id,
                                id=parameters.id,
                                part=parameters.properties_details,
                                maxResults=parameters.max_results,
                                **kwargs)

    def get_videos(self, 
                   parameters: VideoParameters,
                   **kwargs) -> dict[str, any]:
        
        return self._fetch_data(obj_name="videos",
                                op_type="list",
                                id=parameters.id,
                                part=parameters.properties_details,
                                maxResults=parameters.max_results,
                                **kwargs)