from django.db import models

class Rating(models.Model):
    name = models.CharField(max_length=255)

class StreamingPlatform(models.Model):
    name = models.CharField(max_length=255)

class StreamType(models.Model):
    name = models.CharField(max_length=255)

class StreamNumberType(models.Model):
    name = models.CharField(max_length=255)
    number_count = models.IntegerField()

class Stream(models.Model):
    name = models.CharField(max_length=255)
    rating = models.ForeignKey(Rating)
    streaming_platform = models.ForeignKey(StreamingPlatform)
    streaming_platform_ident = models.CharField(max_length=255)
    tl_stream_link = models.CharField(max_length=255)

class Interval(models.Model):
    stream_number_type = models.ForeignKey(StreamNumberType)
    date = models.DateTimeField()

class StreamNumber(models.Model):
    stream = models.ForeignKey(Stream)
    interval = models.ForeignKey(Interval)
    stream_type = models.ForeignKey(StreamType)
    stream_number_type = models.ForeignKey(StreamNumberType)
    number = models.IntegerField()
