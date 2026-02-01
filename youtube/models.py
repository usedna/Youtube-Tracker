from django.db import models
import datetime
from django.utils import timezone


class Channels(models.Model):
    channel_id = models.CharField(max_length=50, 
                                  primary_key=True)
    channel_name = models.CharField(max_length=200,
                                    unique=True,
                                    null=False)
    created_at = models.DateField()
    updated_at = models.DateField()

class Videos(models.Model):
    video_id = models.CharField(max_length=50,
                                primary_key=True)
    channel_id = models.ForeignKey(Channels, on_delete=models.CASCADE)
    video_title = models.CharField(max_length=50)
    duration = models.TimeField()
    uploaded_at = models.DateField()
    
    def __str__(self):
        return self.video_title


class Playlists(models.Model):
    playlist_id = models.CharField(max_length=50,
                                   primary_key=True)
    channl_id = models.ForeignKey(Channels, on_delete=models.CASCADE)
    playlist_title = models.CharField(max_length=200)
    num_of_videos = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    
    def __str__(self):
        return self.playlist_title
    
class PlaylistsVideos(models.Model):
    playlist_id = models.ForeignKey(Playlists, on_delete=models.CASCADE)
    video_id = models.ForeignKey(Videos, on_delete=models.CASCADE)


