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
    
    def get_channels(self,
                     parameters: ChannelParameters,
                    **kwargs) -> dict[str, any]:
                
        try:
            request = self._client.channels().list(id=parameters.id,
                                                      forHandle=parameters.channel_handle,
                                                      part=parameters.properties_details,
                                                      maxResults=parameters.max_results,
                                                     **kwargs)
            response = request.execute()
                        
        except Exception as err:
            response = {"error": err,
                        "context": "channels",}
            
            print(f"Failed to fetch channels: {err}, {type(err)}")
            self._logger.debug(f"Failed to fetch channels: {err}, {type(err)}")
            
        finally:
            return response

    def get_playlists(self,
                      parameters: PlaylistParameters,
                      **kwargs) -> dict[str, any]:
        try:            
            request = self._client.playlists().list(
                                                   channelId=parameters.channel_id,
                                                   id=parameters.id,
                                                   part=parameters.properties_details,
                                                   maxResults=parameters.max_results,
                                                   **kwargs)
            response = request.execute()
            
            save_response_to_file(response, "playlists_response.json")

        except Exception as err:
            response = {"error": err,
                        "context": "playlists",}
            print(f"Failed to fetch playlists: {err}, {type(err)}")
            self._logger.debug(f"Failed to fetch playlists: {err}, {type(err)}")
            
        finally:
            return response

    def get_playlist_items(self,
                           parameters: PlaylistItemParameters,
                           **kwargs) -> dict | None:
        try:
            request = self._client.playlistItems().list(playlistId=parameters.playlist_id,
                                                        id=parameters.id,
                                                        part=parameters.properties_details, 
                                                        maxResults=parameters.max_results,
                                                        **kwargs)
            response = request.execute()

            save_response_to_file(response, "playlist_items_response.json")

        except Exception as err:
            response = {"error": err,
                        "context": "playlist_items",}
            print(f"Failed to fetch playlist items: {err}, {type(err)}")
            self._logger.debug(f"Failed to fetch playlist items: {err}, {type(err)}")
        
        finally:
            return response

    def get_videos(self, 
                   parameters: VideoParameters,
                   **kwargs) -> dict[str, any]:
        try:
            request = self._client.videos().list(part=parameters.properties_details, 
                                                id=parameters.id,
                                                maxResults=parameters.max_results,
                                                **kwargs)
            response = request.execute()
            
            save_response_to_file(response, "videos_response.json")

        except Exception as err:
            response = {"error": err,
                        "context": "videos",}
            print(f"Failed to fetch videos: {err}, {type(err)}")
            self._logger.debug(f"Failed to fetch videos: {err}, {type(err)}")
        
        finally:
            return response
