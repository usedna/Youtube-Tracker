import os

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import googleapiclient.errors
import json


def print_nested_dictionary(req):
    for ch_key in req.keys():
        item = req[ch_key]

        if isinstance(item, dict):
            for key in item:
                print(f"{key}: {item[key]}")
        else:
            print(f"{ch_key}: {item}")


class YTStats:
    def __init__(self, secret_file=None, api_key=None, scopes=[], client=None):
        self.secret_file = secret_file
        self.api_key = api_key
        self.scopes = scopes
        
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.client = client
    
    def create_client(self):
        try:
            if self.secret_file is not None:
                # Get credentials and create an API client
                flow = InstalledAppFlow.from_client_secrets_file(self.secret_file, scopes)
                credentials = flow.run_local_server()
                
            elif self.api_key is not None:
                credentials = None
            
            else:
                raise Exception("The api_key and secret_file are missing")
            
            
            self.client = build(self.api_service_name, 
                                self.api_version, 
                                credentials=credentials,
                                developerKey=self.api_key)
        except FileNotFoundError:
            print(f"Credential file {self.secret_file} not found")
        
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
    
    def get_channel_info(self, channels, properties_details="snippet"):
        try:
            ch_request = self.client.channels().list(forHandle=channels,
                                                     part=properties_details)
            ch_response = ch_request.execute()

            return ch_response

        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            
    def get_playlists(self, channel_name, properties_details="snippet"):
        try:
            channel_id = self.get_channel_info(channel_name, "id")["items"][0]["id"]
            
            request = self.client.playlists().list(part=properties_details, 
                                                   channelId=channel_id,
                                                  )
            response = request.execute()

            return response
        
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            
    def get_playlist_items(self, playlist_id, properties_details="snippet"):
        try:
            request = self.client.playlistItems().list(part=properties_details, 
                                                       playlistId=playlist_id)
            response = request.execute()

            return response
        
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
            
    def get_videos(self, videos_id, properties_details="snippet"):
        try:
            request = self.client.videos().list(part=properties_details, 
                                                id=videos_id)
            response = request.execute()

            return response
        
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")


            
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

yt = YTStats(api_key="AIzaSyC7lXlxXGWqbJb0bR18I5i9uvblj--wc_U", scopes=scopes)
yt.create_client()
channel_details = yt.get_channel_info("janghinaro", properties_details="id")["items"][0]
#playlists = yt.get_playlists(channel_details['id'])
#playlist_items = yt.get_playlist_items("PLiFzfeyzcFOJslV-UXMJaBT739-rJwHn_")
#videos = yt.get_videos("Pk5FMb6JqhQ", "snippet, contentDetails")
#print(videos)
print(channel_details)

    
