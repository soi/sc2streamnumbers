from django.db import models

class StreamType(models.Model):
    name = models.CharField(max_length=255, blank=True)

class Stream(models.Model):
    name = models.CharField(max_length=255, blank=True)

class Interval(models.Model):
    date = models.DateTimeField(auto_now_add=True)

class StreamNumber(models.Model):
    stream = models.ForeignKey(Stream)
    interval = models.ForeignKey(Interval)
    stream_type = models.ForeignKey(StreamType)
    number = models.IntegerField()
