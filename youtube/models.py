from django.db import models
import datetime
from django.utils import timezone


class Video(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    
    def __str__(self):
        return self.title
    
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)



class Playlist(models.Model):
    name = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    
    
    
    def __str__(self):
        return self.name


