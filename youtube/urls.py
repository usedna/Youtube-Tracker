from django.urls import path

from . import views

app_name = "youtube"
urlpatterns = [path("videos/<str:video_id>", views.videos),
               path("playlists/<str:channel_name>", views.playlists)]