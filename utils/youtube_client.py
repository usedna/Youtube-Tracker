from http import client
from common.settings import YT_API_KEY, scopes

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from .youtube_parser import YoutubeAPIParser

class YoutubeClient():
    def __init__(self, secret_file=None, api_key=None, scopes=None):
        self.secret_file = secret_file
        self.api_key = api_key
        self.scopes = scopes
        
        self.api_service_name = "youtube"
        self.api_version = "v3"
        
        self.client = None
        self.parser = None
        
    def create_client(self):
        try:
            if self.secret_file is not None:
                # Get credentials and create an API client
                flow = InstalledAppFlow.from_client_secrets_file(self.secret_file, self.scopes)
                credentials = flow.run_local_server() 
                auth = {"credentials": credentials,}
                
            elif self.api_key is not None:
                auth = {"developerKey": self.api_key,}
            
            else:
                raise Exception("The api_key and secret_file are missing")
            
            self.client = build(self.api_service_name, 
                                self.api_version, 
                                **auth)
        except FileNotFoundError:
            print(f"Credential file {self.secret_file} not found")
        
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            
    def get_client(self):
        return self.client
    
    def create_parser(self):
        try:
            if self.client is None:
                raise Exception("The client is not initialized")
            
            self.parser = YoutubeAPIParser(self.client)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
    
    def get_channel_details(self, channel_name):
        try:
            if self.parser is None:
                raise Exception("The parser is not initialized")
            
            ch_response = self.parser.parse_channel_info(channel_name)
            
            return ch_response
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            
    def get_playlists(self, channel_id=None, channel_name=None):
        try:
            if self.parser is None:
                raise Exception("The parser is not initialized")
            
            pl_response = self.parser.parse_playlists_info(channel_id=channel_id, 
                                                           channel_name=channel_name)
            
            return pl_response
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            
    def get_playlist_items(self, playlist_id):
        try:
            if self.parser is None:
                raise Exception("The parser is not initialized")
            
            pi_response = self.parser.parse_playlist_items_info(playlist_id)
            
            return pi_response
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            
    def get_videos(self, videos_id):
        try:
            if self.parser is None:
                raise Exception("The parser is not initialized")
            
            vd_response = self.parser.parse_videos_info(videos_id)
            
            return vd_response
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")


def get_youtube_client():
    client = YoutubeClient(api_key=YT_API_KEY, scopes=scopes)
    client.create_client()
    client.create_parser()
    return client