from api_client.service.youtube_service import YoutubeDataService
from api_client.service.youtube_parser import YoutubeAPIDataParser
from api_client.service.youtube_client import YoutubeAPIClient
from api_client.utils import create_client
from api_client.models import parameters


def create_service(api_key: str|None = None,
                   auth_file: str|None = None, 
                   scopes: list = []) -> YoutubeDataService:
    client = create_client(api_key=api_key, secret_file=auth_file, scopes=scopes)
    parser = YoutubeAPIDataParser()
    api_client = YoutubeAPIClient(client)
    service = YoutubeDataService(api_client, parser)
    return service


def get_channels_by_id(service: YoutubeDataService, 
                       channel_ids: list[str],
                       properties: list[str]|str|None = None,
                       max_results: int = 50,
                       **kwargs) -> list[dict]:
    
    channels_count = len(channel_ids)
    
    if max_results > 50 or channels_count >= 50:
        max_results = 50
    
    elif channels_count > max_results:
        max_results = channels_count
        
    parameters = parameters.ChannelParameters(id=channel_ids,
                                              properties_details=properties,
                                              max_results=max_results,
                                              **kwargs)
        
    if channels_count > 50:
        results = []
        for i in range(0, channels_count, 50):
            parameters.id = channel_ids[i:i+50]
            result = service.get_channel_details(parameters)
            results.extend(result)
    else:
        results = service.get_channel_details(parameters)
    
    return results

def get_channels_by_handle(service: YoutubeDataService,
                           channel_handles: list[str],
                           properties: list[str]|str|None = None,
                           max_results: int = 50,
                           **kwargs) -> list[dict]:
    results = []
    
    if max_results > 50 or max_results <= 0:
        max_results = 50
    
    for handle in channel_handles:
        parameter = parameters.ChannelParameters(channel_handle=handle,
                                                 properties_details=properties,
                                                 max_results=max_results,
                                                 **kwargs)
        results.extend(service.get_channel_details(parameter))
        
    return results

def get_playlists_by_channel_id(service: YoutubeDataService,
                                channel_ids: str,
                                properties: list[str]|str|None = None,
                                max_results: int = 50,
                                fetch_all: bool = False,
                                **kwargs) -> list[dict]:
    
    results = []

    
    if max_results > 50 or max_results <= 0 or fetch_all:
        max_results = 50
    
    for channel_id in channel_ids:
        parameter = parameters.PlaylistParameters(channel_id=channel_id,
                                                  properties_details=properties,
                                                  max_results=max_results,
                                                  **kwargs)
        
        result = service.get_playlists(parameter)
        
        if fetch_all:
            items, _, next_page_token = result
            results.extend(items)
            
            while next_page_token:
                parameter.page_token = next_page_token
                items, _, next_page_token = service.get_playlists(parameter)
                results.extend(items)
        else:          
            results.append(result)
        
    return results

def get_playlist_items_by_id(service: YoutubeDataService,
                                      item_ids: list[str],
                                      properties: list[str]|str|None = None,
                                      max_results: int = 50,
                                      **kwargs) -> list[dict]:
    
    items_count = len(item_ids)
    
    if max_results > 50 or items_count >= 50:
        max_results = 50
    
    elif items_count > max_results:
        max_results = items_count
    
    parameter = parameters.PlaylistItemParameters(id=item_ids,
                                                  properties_details=properties,
                                                  max_results=max_results,
                                                  **kwargs)
    
    if items_count > 50:
        results = []
        for i in range(0, items_count, 50):
            parameters.id = item_ids[i:i+50]
            result = service.get_playlist_items(parameters)
            results.extend(result)
    else:
        results = service.get_playlist_items(parameter)
    
    return results

def get_playlist_items_by_playlist_id(service: YoutubeDataService,
                                      playlist_ids: list[str],
                                      properties: list[str]|str|None = None,
                                      max_results: int = 50,
                                      fetch_all: bool = False,
                                      **kwargs) -> list[dict]:
    
    results = []
        
    if max_results > 50 or max_results <= 0 or fetch_all:
        max_results = 50
    
    for playlist_id in playlist_ids:
        parameter = parameters.PlaylistItemParameters(playlist_id=playlist_id,
                                                      properties_details=properties,
                                                      max_results=max_results,
                                                      **kwargs)
        
        
        result = service.get_playlist_items(parameter)
        
        if fetch_all:
            items, _, next_page_token = result
            results = items
            
            while next_page_token:
                parameter.page_token = next_page_token
                items, _, next_page_token = service.get_playlist_items(parameter)
                results.extend(items)
        else:
            results.append(result)
    
    return results

def get_videos_by_id(service: YoutubeDataService,
                     video_ids: list[str],
                     properties: list[str]|str|None = None,
                     max_results: int = 50,
                     **kwargs) -> list[dict]:
    
    videos_count = len(video_ids)
    
    if max_results > 50 or videos_count >= 50:
        max_results = 50
    
    elif videos_count > max_results:
        max_results = videos_count
    
    parameter = parameters.VideoParameters(id=video_ids,
                                           properties_details=properties,
                                           max_results=max_results,
                                           **kwargs)
    
    if videos_count > 50:
        results = []
        for i in range(0, videos_count, 50):
            parameters.id = video_ids[i:i+50]
            result = service.get_videos(parameter)
            results.extend(result)
    else:
        results = service.get_videos(parameter)
    
    return results