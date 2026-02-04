from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db import IntegrityError, transaction

from .models import Videos, Playlists, Channels
from utils.youtube_client import get_youtube_client
import json


client = get_youtube_client()

def channels(request, channel_name):
    try:
        channel_details = client.get_channel_details(channel_name)
        
        if channel_details is None:
            raise Exception("Channel not found")
        
        with transaction.atomic():

            channels_db = Channels.objects.bulk_create([Channels(channel_id=channel_id, 
                                                                **channel_details[channel_id]["details"])
                                                      for channel_id in channel_details.keys()])
            
        return JsonResponse(channel_details)
    except IntegrityError:
        return JsonResponse({"error": "error",
                             "msg": "Channel already exists in the database"}, 
                            status=400)
    
    except Exception as err:
        print(f"ERROR: Failed to add channels: {err}, {type(err)}")
        return JsonResponse({"error": "error",
                             "msg": "Channel not found"}, status=404)

# TODO: Add channel_id parameter
def channel_playlists(request, channel_name):
    try:    
        if not Channels.objects.filter(channel_name=channel_name).exists():
            channel_details = channels(request, channel_name)
            
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

# TODO: Add use playlist name
def playlist_videos(request, playlist_id):
    try:
        # TODO: Implement database
        
        playlist_items = client.get_playlist_items(playlist_id)
        return JsonResponse(playlist_items)
    except Exception as err:
        return JsonResponse({"error": str(err),
                             "msg": "Playlist items not found"}, 
                            status=404)
        
def videos(request, video_id):
    try:
        # TODO: Implement database
        
        video_details = client.get_videos(video_id)
        return JsonResponse(video_details)
    except Exception as err:
        return JsonResponse({"error": str(err),
                             "msg": "Video not found"}, 
                            status=404)



