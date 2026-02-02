import os

class YoutubeAPI():
    def __init__(self, client=None):
        self.client = client
    
    def get_channels(self, 
                     channels, 
                     properties_details="snippet", 
                     max_results=5,
                     **kwargs):
        try:
            ch_request = self.client.channels().list(forHandle=channels,
                                                     part=properties_details,
                                                     maxResults=max_results,
                                                     **kwargs)
            ch_response = ch_request.execute()

            return ch_response

        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            
    def get_playlists(self, 
                      channel_id, 
                      properties_details="snippet", 
                      max_results=5, 
                      **kwargs):
        try:            
            request = self.client.playlists().list(part=properties_details, 
                                                   channelId=channel_id,
                                                   maxResults=max_results,
                                                   **kwargs)
            response = request.execute()

            return response
        
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            
    def get_playlist_items(self, 
                           playlist_id, 
                           properties_details="snippet", 
                           max_results=5, 
                           **kwargs):
        try:
            request = self.client.playlistItems().list(part=properties_details, 
                                                       playlistId=playlist_id,
                                                       maxResults=max_results,
                                                       **kwargs)
            response = request.execute()

            return response
        
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            
    def get_videos(self, 
                   videos_id, 
                   properties_details="snippet", 
                   max_results=5, 
                   **kwargs):
        try:
            request = self.client.videos().list(part=properties_details, 
                                                id=videos_id,
                                                maxResults=max_results,
                                                **kwargs)
            response = request.execute()

            return response
        
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
