from django.db import models

class StreamType(models.Model):
    name = models.CharField(max_length=255)

class Stream(models.Model):
    name = models.CharField(max_length=255)

class StreamNumberType(models.Model):
    name = models.CharField(max_length=255)
    number_count = models.IntegerField()

class Interval(models.Model):
    date = models.DateTimeField()
    stream_number_type = models.ForeignKey(StreamNumberType)

class StreamNumber(models.Model):
    stream = models.ForeignKey(Stream)
    interval = models.ForeignKey(Interval)
    stream_type = models.ForeignKey(StreamType)
    stream_number_type = models.ForeignKey(StreamNumberType)
    number = models.IntegerField()
