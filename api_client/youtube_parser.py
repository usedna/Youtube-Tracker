
import isodate
from api_client.models import channel, playlist, video

class YoutubeAPIDataParser():      
    def parse_channel_info(self, api_response: dict[str, any]) -> list[channel.Channel]:
        channels = []
        
        for item in api_response["items"]:
            snippet = item["snippet"]
            banner = item["brandingSettings"]
            statistics = item["statistics"].values()
            topics = item["topicDetails"].values()
            status = item["status"].values()
            
            channel_data = channel.Channel(channel.Details(channel_id=item["id"],
                                                           uploads_id=item["contentDetails"]["relatedPlaylists"]["uploads"],
                                                           channel_name=snippet["title"],
                                                           etag=item["etag"],
                                                           description=snippet["description"],
                                                           created_at=snippet["publishedAt"],
                                                           country=snippet["country"],),
                                           channel.Statistics(*statistics),
                                           channel.Topics(*topics),
                                           channel.Thumbnails(**snippet["thumbnails"]),
                                           channel.BannerImage(banner_image_url=banner["image"]["bannerExternalUrl"],),
                                           channel.Keywords(keywords=banner["channel"]["keywords"],),
                                           channel.Status(*status))
            
            channels.append(channel_data)

        return channels
    
    def parse_playlists_info(self, api_response: dict[str, any]) -> playlist.Playlists:
        playlists = []
        total_results = api_response["pageInfo"]["totalResults"],

        for item in api_response["items"]:
            snippet = item["snippet"]
            
            playlist_data = playlist.Playlist(playlist.Details(playlist_id=item["id"],
                                                               playlist_title=snippet["title"],
                                                               videos_count=int(item["contentDetails"]["itemCount"]),
                                                               description=snippet["description"],
                                                               created_at=snippet["publishedAt"],),
                                              playlist.ItemThumbnails(**snippet["thumbnails"]),
                                              playlist.Status(privacy_status=item["status"]["privacyStatus"],),)
                         
            playlists.append([playlist_data])
            
        return playlist.Playlists(playlists=playlists, 
                                  playlists_count=total_results)
    
    def parse_playlist_items_info(self, api_response: dict[str, any]) -> playlist.PlaylistItems:            
        items = []
        total_results = api_response["pageInfo"]["totalResults"],
        
        for item in api_response["items"]:
            snippet = item["snippet"]
            
            item = playlist.Item(video.VideoBasicDetails(video_id=snippet["resourceId"]["videoId"],
                                                         video_title=snippet["title"],
                                                         video_description=snippet["description"],
                                                         uploaded_at=item["contentDetails"]["videoPublishedAt"],),
                                   playlist.ItemDetails(item_id=item["id"],
                                                        position=snippet["position"],
                                                        published_at=snippet["publishedAt"],),
                                   playlist.ItemThumbnails(**snippet["thumbnails"]),)

            items.append(item)
            
        return playlist.PlaylistItems(items=items,
                                      items_count=total_results)
 
    def parse_videos_info(self, api_response: dict[str, any]) -> list[video.Video]:
        
        for item in api_response["items"]:
            videos = []
            snippet = item["snippet"]
            content_details = item["contentDetails"]
            statistics = item["statistics"].values()
            status = item["status"].values()
            duration = str(isodate.parse_duration(content_details["duration"]))
            
            video_data = video.Video(video.VideoDetails(video_id=item["id"],
                                                        video_title=snippet["title"],
                                                        video_description=snippet["description"],
                                                        uploaded_at=snippet["publishedAt"],
                                                        etag=item["etag"],
                                                        duration=duration,
                                                        language=snippet["defaultLanguage"],
                                                        tags=snippet["tags"],
                                                        dimension=content_details["dimension"],
                                                        definition=content_details["definition"],
                                                        paid=item["paidProductPlacementDetails"]["hasPaidProductPlacement"],
                                                        caption=content_details["caption"],),
                                        video.Statistics(*statistics),
                                        video.Topics(categories=item["topicDetails"]["topicCategories"],),
                                        video.Status(*status),
                                        )
            videos.append(video_data)

        return videos
    