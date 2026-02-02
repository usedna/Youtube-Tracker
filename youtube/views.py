from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Videos, Playlists
from utils.youtube_client import get_youtube_client
import json


client = get_youtube_client()

def channels(request, channel_name):
    try:
        # TODO: Implement database
        
        channel_details = client.get_channel_details(channel_name)
        return JsonResponse(channel_details)
    except Exception as err:
        return JsonResponse({"error": str(err),
                             "msg": "Channel not found"}, status=404)

# TODO: Add channel_id parameter
def channel_playlists(request, channel_name):
    try:
        # TODO: Implement database
        
        playlists = client.get_playlists(channel_name=channel_name)
        return JsonResponse(playlists)
    except Exception as err:
        return JsonResponse({"error": str(err),
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



