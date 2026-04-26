from django.urls import path

from . import views

app_name = "youtube"
urlpatterns = [
               path("channel/<str:handle>", views.Channel.as_view(), name="channel-by-handle"),
               path("channel/<str:id>", views.Channel.as_view(), name="channel-by-id"),
               path("channel-playlists/<str:channel_name>", views.channel_playlists),
               path("playlist-videos/<str:playlist_id>", views.playlist_videos),
               path("video/<str:video_id>", views.video),
               path("index", views.index)
               ]