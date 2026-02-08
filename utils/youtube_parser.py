from utils.youtube_data import YoutubeAPI
import isodate

class YoutubeAPIParser():
    def __init__(self, youtube_client):
        self.youtube_api = YoutubeAPI(youtube_client)
                
    def parse_channel_info(self, channel_name):
        try:
            if channel_name is None:
                raise Exception("Channel name is missing")
                   
            api_response = self.youtube_api.get_channels(channel_name, 
                                                         properties_details="id,snippet,statistics,topicDetails,\
                                                                             contentDetails,brandingSettings,\
                                                                             status,contentOwnerDetails,localizations", 
                                                         max_results=1)
            if api_response is None:
                raise Exception("ERROR: API request failed")
            
            if "items" not in api_response or not len(api_response["items"]):
                return None
            
            channel = {item["id"] : {"details": {"etag": item["etag"],
                                                 "channel_name": item["snippet"]["title"],
                                                 "channel_description": item["snippet"]["description"],
                                                 "created_at": item["snippet"]["publishedAt"],
                                                 "country": item["snippet"]["country"],},
                                     "statistics": {"views": item["statistics"]["viewCount"],
                                                    "subscribers": item["statistics"]["subscriberCount"],
                                                    "videos": item["statistics"]["videoCount"],},
                                     "topics": {"topic_ids": item["topicDetails"]["topicIds"],
                                                "topic_categories": item["topicDetails"]["topicCategories"]},
                                     "thumbnails": item["snippet"]["thumbnails"],
                                     "banner_image": item["brandingSettings"]["image"],
                                     "keywords": item["brandingSettings"]["channel"]["keywords"]} 
                   for item in api_response["items"]}

            return channel
        
        except Exception as err:
            print(f"ERROR: Unexpected {err}, {type(err)}")
            return None
    
    def parse_playlists_info(self, channel_id=None):
        playlists = {}
        
        try:
            if channel_id is None:
                raise Exception("Channel ID is missing")
            
            api_response = self.youtube_api.get_playlists(channel_id=channel_id,
                                                          properties_details="id,snippet,contentDetails,localizations,player,status",
                                                          max_results=25)
            
            if api_response is None:
                raise Exception("ERROR: API request failed")
            
            if "items" not in api_response or not len(api_response["items"]):
                return None
            
            playlists["playlists"] = {item["id"]: {"details": {"playlist_title": item["snippet"]["title"],
                                                               "description": item["snippet"]["description"],
                                                               "videos_count": item["contentDetails"]["itemCount"],
                                                               "created_at": item["snippet"]["publishedAt"],
                                                               },
                                                   "status": item["status"],
                                                   }
                                      for item in api_response["items"]}
            
            playlists.update({"playlists_count": api_response["pageInfo"]["totalResults"]})
            
            return api_response
        
        except Exception as err:
            print(f"ERROR: Unexpected {err}, {type(err)}")
    
    def parse_playlist_items_info(self, playlist_id):
        try:
            api_response = self.youtube_api.get_playlist_items(playlist_id, 
                                                               properties_details="id,snippet,contentDetails,status",
                                                               max_results=25)
            
            items = {item["id"]: {"video_details": {"video_id": item["snippet"]["resourceId"]["videoId"],
                                                    "video_title": item["snippet"]["title"],
                                                    "video_description": item["snippet"]["description"],
                                                    "uploaded_at": item["contentDetails"]["videoPublishedAt"],},
                                  "item":{"position": item["snippet"]["position"],
                                          "published_at": item["snippet"]["publishedAt"],},
                                  "thumbnails": item["snippet"]["thumbnails"]
            }
                     for item in api_response["items"]}
            
            #items.update({"items_count": api_response["pageInfo"]["totalResults"]})

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
                                                       max_results=25)
            
            videos = {item["id"]: {"video_details": {"etag": item["etag"],
                                                     "video_title": item["snippet"]["title"],
                                                     "duration": str(isodate.parse_duration(item["contentDetails"]["duration"])),
                                                     "video_description": item["snippet"]["description"],
                                                     "language": item["snippet"]["defaultLanguage"],
                                                     "tags": item["snippet"]["tags"],
                                                     "dimension": item["contentDetails"]["dimension"],
                                                     "definition": item["contentDetails"]["definition"],
                                                     "paid": item["paidProductPlacementDetails"]["hasPaidProductPlacement"],
                                                     "uploaded_at": item["snippet"]["publishedAt"],},
                                   "statistics": {"views": item["statistics"]["viewCount"],
                                                  "likes": item["statistics"]["likeCount"],
                                                  "comments": item["statistics"]["commentCount"],},
                                   "channel_id": item["snippet"]["channelId"],
                                 }
                     for item in api_response["items"]}

            return videos
        
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
    