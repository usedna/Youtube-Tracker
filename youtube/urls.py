from django.urls import path

from . import views

app_name = "youtube"
urlpatterns = [path("channels/<str:channel_name>", views.channels),
               path("videos/<str:video_id>", views.videos),
               path("channel-playlists/<str:channel_name>", views.channel_playlists),
               path("playlist-videos/<str:playlist_id>", views.playlist_videos),
               ]