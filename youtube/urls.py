from django.urls import path

from . import views

app_name = "youtube"
urlpatterns = [path("channel/<str:channel_name>", views.channel),
               path("channel-playlists/<str:channel_name>", views.channel_playlists),
               path("playlist-videos/<str:playlist_id>", views.playlist_videos),
               path("video/<str:video_id>", views.video),
               path("index", views.index)
               ]