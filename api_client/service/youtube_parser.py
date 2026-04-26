
import isodate
from api_client.models import channel, playlist, video

class YoutubeAPIDataParser():      
    def parse_channel_info(self, 
                           api_response: dict[str, any],
                           raw: bool = True) -> list[channel.Channel]:
        result = []
        
        for item in api_response["items"]:
            snippet = item["snippet"]
            banner = item["brandingSettings"]
            statistics = item["statistics"].values()
            topics = item["topicDetails"].values()
            status = item["status"].values()
            
            channel_data = channel.Channel(channel.Details(channel_id=item["id"],
                                                           uploads_id=item["contentDetails"]["relatedPlaylists"]["uploads"],
                                                           channel_handle=snippet["customUrl"],
                                                           channel_name=snippet["title"],
                                                           etag=item["etag"],
                                                           channel_description=snippet["description"],
                                                           created_at=snippet["publishedAt"],
                                                           country=snippet["country"],),
                                           statistics=channel.Statistics(*statistics),
                                           topics=channel.Topics(*topics),
                                           thumbnails=channel.Thumbnails(**snippet["thumbnails"]),
                                           banner_image=channel.BannerImage(banner_image_url=banner["image"]["bannerExternalUrl"],),
                                           keywords=channel.Keywords(keywords=banner["channel"]["keywords"],),
                                           status=channel.Status(*status),
                                           )
            
            result.append(channel_data if not raw else channel_data.to_dict())

        return result

    def parse_playlists_info(self, api_response: dict[str, any],
                             raw: bool = True) -> playlist.Playlists:
        playlists = []
        total_results = api_response["pageInfo"]["totalResults"]
        next_page_token = api_response.get("nextPageToken")

        for item in api_response["items"]:
            snippet = item["snippet"]
            
            playlist_data = playlist.Playlist(playlist.Details(playlist_id=item["id"],
                                                               playlist_title=snippet["title"],
                                                               videos_count=int(item["contentDetails"]["itemCount"]),
                                                               description=snippet["description"],
                                                               created_at=snippet["publishedAt"],),
                                              playlist.ItemThumbnails(**snippet["thumbnails"]),
                                              playlist.Status(privacy_status=item["status"]["privacyStatus"],),)
                         
            playlists.append(playlist_data if not raw else playlist_data.to_dict())
        
        results = playlist.Playlists(playlists=playlists, 
                                     playlists_count=total_results,
                                     next_page_token=next_page_token)
        
        if raw:
            return results.to_dict()
        
        return result
    
    def parse_playlist_items_info(self, api_response: dict[str, any],
                                  raw: bool = True) -> playlist.PlaylistItems:            
        items = []
        total_results = api_response["pageInfo"]["totalResults"]
        next_page_token = api_response.get("nextPageToken")
        
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

            items.append(item if not raw else item.to_dict())
        
        result = playlist.PlaylistItems(items=items, 
                                        items_count=total_results,
                                        next_page_token=next_page_token)
        
        if raw:
            return result.to_dict()
        
        return result
 
    def parse_videos_info(self, api_response: dict[str, any],
                          raw: bool = True) -> list[video.Video]:
        
        results = []
        
        for item in api_response["items"]:
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
            results.append(video_data if not raw else video_data.to_dict())
        
        return results
    