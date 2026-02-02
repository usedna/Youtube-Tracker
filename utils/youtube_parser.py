from utils.youtube_data import YoutubeAPI

class YoutubeAPIParser():
    def __init__(self, youtube_client):
        self.youtube_api = YoutubeAPI(youtube_client)
                
    def parse_channel_info(self, channel_name):
        try:            
            api_response = self.youtube_api.get_channels(channel_name, 
                                                         properties_details="id,snippet,statistics,topicDetails,\
                                                                             contentDetails,brandingSettings,\
                                                                             status,contentOwnerDetails,localizations", 
                                                         max_results=1)
            if api_response is None:
                raise Exception("ERROR: API request failed")
            
            if "items" not in api_response:
                return None
            
            channel = {item["id"] : {"etag": item["etag"],
                                 "title": item["snippet"]["title"],
                                 "description": item["snippet"]["description"],
                                 "created_at": item["snippet"]["publishedAt"],
                                 "country": item["snippet"]["country"],
                                 "views": item["statistics"]["viewCount"],
                                 "subscribers": item["statistics"]["subscriberCount"],
                                 "videos": item["statistics"]["videoCount"],
                                 "topics": item["topicDetails"]["topicCategories"]} 
                   for item in api_response["items"]}

            return channel
        
        except Exception as err:
            print(f"ERROR: Unexpected {err}, {type(err)}")
            return None
    
    def parse_playlists_info(self, channel_id=None, channel_name=None):
        playlists = {}
        
        try:
            if channel_id is None:
                if channel_name is None:
                    raise Exception("Both channel_id and channel_name are missing")
                
                channel = self.parse_channel_info(channel_name)
                
                # TODO: Handle multiple channels returned
                channel_id = list(channel.keys())[0]
            
            api_response = self.youtube_api.get_playlists(channel_id=channel_id,
                                                         properties_details="id,snippet,contentDetails,localizations,player,status",
                                                         max_results=1)
            
            playlists["playlists"] = {item["id"]: {"etag": item["etag"],
                                                   "channelId": item["snippet"]["channelId"],
                                                   "title": item["snippet"]["title"],
                                                   "description": item["snippet"]["description"],
                                                   "created_at": item["snippet"]["publishedAt"],
                                                   "item_count": item["contentDetails"]["itemCount"],
                                                   "status": item["status"],
                                                    }
                                      for item in api_response["items"]}
            
            playlists.update({"playlists_count": api_response["pageInfo"]["totalResults"]})
            
            if channel_name is not None:
                playlists.update({"channels_data": channel})
            
            return playlists
        
        except Exception as err:
            print(f"ERROR: Unexpected {err}, {type(err)}")
    
    def parse_playlist_items_info(self, playlist_id):
        try:
            api_response = self.youtube_api.get_playlist_items(playlist_id, 
                                                               properties_details="id,snippet,contentDetails,status",
                                                               max_results=1)
            
            items = {item["id"]: {"videoId": item["snippet"]["resourceId"]["videoId"],
                                  "channelId": item["snippet"]["channelId"],
                                  "playlistId": item["snippet"]["playlistId"],
                                  "video_title": item["snippet"]["title"],
                                  "description": item["snippet"]["description"],
                                  "position": item["snippet"]["position"],
                                  "published_at": item["snippet"]["publishedAt"],
                                  "video_published_at": item["contentDetails"]["videoPublishedAt"]
                                 }
                     for item in api_response["items"]}
            
            return items
        
        except Exception as err:
            print(f"ERROR: Unexpected {err}, {type(err)}")
    
    def parse_videos_info(self, videos_id):
        try:
            api_response = self.youtube_api.get_videos(videos_id, 
                                                       properties_details="contentDetails,id,liveStreamingDetails,\
                                                                           localizations,paidProductPlacementDetails,player,\
                                                                           recordingDetails,snippet,\
                                                                           statistics,status,topicDetails",
                                                       max_results=1)
            
            videos = {item["id"]: {"etag": item["etag"],
                                   "channelId": item["snippet"]["channelId"],
                                   "title": item["snippet"]["title"],
                                   "description": item["snippet"]["description"],
                                   "duration": item["contentDetails"]["duration"],
                                   "dimension": item["contentDetails"]["dimension"],
                                   "definition": item["contentDetails"]["definition"],
                                   "default_language": item["snippet"]["defaultLanguage"],
                                   "tags": item["snippet"]["tags"],
                                   "paid": item["paidProductPlacementDetails"]["hasPaidProductPlacement"],
                                   "published_at": item["snippet"]["publishedAt"],
                                   "views": item["statistics"]["viewCount"],
                                   "likes": item["statistics"]["likeCount"],
                                   "comments": item["statistics"]["commentCount"],
                                 }
                     for item in api_response["items"]}

            return videos
        
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
    