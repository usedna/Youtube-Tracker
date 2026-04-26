from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.views import View

from .models import Videos, Playlists, Channels, PlaylistsVideos
from api_client.models import parameters
from api_client.youtube_service import get_youtube_service
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
import datetime


client = get_youtube_service()

# TODO: Use channel id parameter
@method_decorator(csrf_exempt, name='dispatch')
class Channel(View):
    model = Channels
    
    @staticmethod
    def get_parameters(**kwargs):
        channel_handle = kwargs.get("handle", None)
        channel_id = kwargs.get("id", None)  
        print(f"Received parameters: channel_handle={channel_handle is None}, channel_id={channel_id is None}")
        if channel_handle is None and channel_id is None:
            raise ValueError("At least one of channel handle or channel id must be provided")
  
        return channel_handle, channel_id
        
    def post(self, request, **kwargs):
        try:
            channel_handle, channel_id = self.get_parameters(**kwargs)

            channel_details = client.get_channel_details(parameters=parameters.ChannelParameters(channel_handle=channel_handle,
                                                                                                 id=channel_id))

            if channel_details is None:
                raise Exception("Channel not found")

            with transaction.atomic():
                print(f"Saving channel details to the database:", channel_details[0]["details"])
                _ = Channels.objects.bulk_create([Channels(**channel["details"])
                                                          for channel in channel_details],
                                                          ignore_conflicts=True)
                
            return JsonResponse({"msg": channel_details})
        except IntegrityError:
            return JsonResponse({"error": "error",
                                 "msg": "Channel already exists in the database"}, 
                                status=400)

        except Exception as err:
            print(f"ERROR: Failed to add channels: {err}, {type(err)}")
            return JsonResponse({"error": "error",
                                 "msg": "Channel not found"}, status=404)
    
    def get(self, request, **kwargs):
        try:
            channel_handle, channel_id = self.get_parameters(**kwargs)
            
            channel = self.model.objects.get(channel_name="janghinaro")
            print(f"Channel found in the database: {channel}")
            return JsonResponse({"channel": dict(channel)})
            
        except Exception as err:
            print(f"ERROR: Failed to fetch channel details: {err}, {type(err)}")
            return JsonResponse({"error": "error",
                                 "msg": "Channel not found"}, 
                                  status=404)
    
# TODO: Add channel_id parameter
def channel_playlists(request, channel_name: str|None=None, channel_id: str|None=None):
    try:    
        if not Channels.objects.filter(channel_name=channel_name).exists():
            channel_details = channel(request, channel_name)
            
            if channel_details.status_code == 404:
                raise Exception("Channel not found")
        
        channel = Channels.objects.get(channel_name=channel_name)
        
        playlists = client.get_playlists(channel_id=channel.channel_id)
        
        with transaction.atomic():
            playlists_details = playlists["playlists"]
            
            playlists_db = Playlists.objects.bulk_create([Playlists(playlist_id=playlist_id,
                                                                    channel_id=channel,
                                                                    **playlists_details[playlist_id]["details"])
                                                         for playlist_id in playlists_details.keys()],
                                                         ignore_conflicts=True)
        
        return JsonResponse(playlists_details)
    
    except IntegrityError:
        return JsonResponse({"error": "error",
                             "msg": "Channel already exists in the database"}, 
                            status=400)
    
    except Exception as err:
        print(f"ERROR: Unexpected {err}, {type(err)}")
        return JsonResponse({"error": "error",
                             "msg": "Playlists not found"}, 
                            status=404)


def playlist_videos(request, playlist_id: str):
    try:
        
        playlist_db = get_object_or_404(Playlists, playlist_id=playlist_id)
        
        playlist_items = client.get_playlist_items(playlist_id)

        with transaction.atomic():
            for item_id in playlist_items.keys():
                video_db=Videos(channel_id=playlist_db.channel_id,
                                duration="00:00",
                                **playlist_items[item_id]["video_details"],
                                )
                video_db.save()
                
                playlist_videos_db = PlaylistsVideos(playlist_id=playlist_db,
                                                     video_id=video_db,
                                                     **playlist_items[item_id]["item"])
                playlist_videos_db.save()
            
        return JsonResponse(playlist_items)
    
    except Exception as err:
        print(err, type(err))
        return JsonResponse({"error": str(err),
                             "msg": "Playlist items not found"}, 
                            status=404)
        
def video(request, video_id: str):
    try:
        video_details = {}
        
        if not Videos.objects.filter(video_id=video_id).exists():
            video_db = None
            duration = 0
        else:
            video_db = Videos.objects.get(video_id=video_id)
            duration = datetime.timedelta(hours=video_db.duration.hour,
                                          minutes=video_db.duration.minute,
                                          seconds=video_db.duration.second).total_seconds()
            
        if video_db is None or not duration:
            video_details = client.get_videos(video_id)
        
            for video_id in video_details.keys():
                channel_id = video_details[video_id]["channel_id"]

                if not Channels.objects.filter(channel_id=channel_id).exists():
                    channel_details = channel(request, channel_id)

                    if channel_details.status_code == 404:
                        raise Exception("Channel not found")

                channel_db = Channels.objects.get(channel_id=channel_id)
                with transaction.atomic():
                    if video_db is None:
                        video_db = Videos(video_id=video_id,
                                          channel_id=channel_db,
                                          **video_details[video_id]["video_details"])

                    else:
                        video_db.__dict__.update(video_details[video_id]["video_details"])
                        video_db.save()

        return JsonResponse(video_details)
    except Exception as err:
        return JsonResponse({"error": str(err),
                             "msg": "Video not found"}, 
                            status=404)


def index(request):
    return render(request, "index.html")

