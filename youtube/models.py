from django.db import models
import datetime
from django.utils import timezone
import uuid


class Channels(models.Model):
    channel_id = models.CharField(max_length=30, 
                                  primary_key=True)
    channel_name = models.CharField(max_length=50,
                                    unique=True,
                                    null=False)
    etag = models.CharField(max_length=100)
    channel_description = models.TextField()
    created_at = models.DateTimeField()
    country = models.CharField(max_length=10)

    def __str__(self):
        return self.channel_name


class Playlists(models.Model):
    playlist_id = models.CharField(max_length=50,
                                   primary_key=True)
    channel_id = models.ForeignKey(Channels, on_delete=models.CASCADE, to_field='channel_id')
    playlist_title = models.CharField(max_length=200)
    description = models.TextField(default="")
    videos_count = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    
    def __str__(self):
        return self.playlist_title


class Videos(models.Model):
    video_id = models.CharField(max_length=20,
                                primary_key=True)
    channel_id = models.ForeignKey(Channels, on_delete=models.CASCADE, to_field='channel_id')
    etag = models.CharField(max_length=100)
    video_title = models.CharField(max_length=100)
    duration = models.TimeField()
    video_description = models.TextField(default="")
    language = models.CharField(max_length=5, default="")
    tags = models.TextField(default="")
    dimension = models.CharField(max_length=5, default="")
    definition = models.CharField(max_length=5, default="")
    paid = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField()

    def __str__(self):
        return self.video_title

class PlaylistsVideos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    playlist_id = models.ForeignKey(Playlists, on_delete=models.CASCADE)
    video_id = models.ForeignKey(Videos, on_delete=models.CASCADE)
    position = models.IntegerField()
    published_at = models.DateTimeField()
