from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Videos, Playlists
from utils.youtube import yt
import json


def channels(request, channel_name):
    try:
        channel_details = yt.get_channel_info(channel_name)
        return HttpResponse(json.dumps(video_details))
    except Exception as err:
        return Http404()

def videos(request, video_id):
    try:
        video_details = yt.get_videos("Pk5FMb6JqhQ", properties_details="contentDetails")["items"][0]
        return HttpResponse(json.dumps(video_details))
    except Exception as err:
        return Http404()
    
def playlists(request, channel_name):
    try:
        playlists = yt.get_playlists("janghinaro", "id,contentDetails")["items"]
        return HttpResponse(json.dumps(playlists))
    except Exception as err:
        return Http404()



