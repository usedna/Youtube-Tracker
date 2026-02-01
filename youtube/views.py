from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Video, Playlist


class VideoView(generic.ListView):
    template_name = "polls/video.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Video.objects.order_by("-pub_date")[:5]
    
class PlaylistView(generic.ListView):
    template_name = "youtube/video.html"
    context_object_name = "latest_question_list"
    
    def get_playlist(self):
        return HttpResponse("No Playlist")



