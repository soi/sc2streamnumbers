import json
import time
import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.contrib.sites.models import Site

from streams.main.models import Stream, Interval, StreamNumber

def homepage(request):
    latest_interval = Interval.objects.order_by('-date')[0]
    stream_numbers= StreamNumber.objects.select_related() \
        .filter(interval=latest_interval).order_by('-number')
    return render_to_response('homepage.html',
                              {
                                'stream_numbers': stream_numbers,
                                'interval': latest_interval
                              },
                              context_instance=RequestContext(request))

def detail(request, stream_id):
    try:
        stream = Stream.objects.get(pk=stream_id)
        current_site = Site.objects.get_current()
    except Stream.DoesNotExist:
        raise Http404
    return render_to_response('detail.html',
                              {
                                'stream': stream,
                                'current_site': current_site
                              },
                              context_instance=RequestContext(request))

def stream_numbers(request, stream_id, time_span):
    def get_stream_numbers(stream, min_time):
        return StreamNumber.objects \
                           .filter(stream=stream,
                                   interval__date__gt=min_time) \
                           .order_by('interval__date')

    def get_snum_dict(stream_numbers):
        return_arr = []
        for snum in stream_numbers:
            unix_time = int(snum.interval.date.strftime("%s"))
            return_arr.append({
                                'date': unix_time,
                                'number': snum.number
                              })
        return return_arr

    time_spans = ['hour', 'day', 'week', 'month', 'year', 'forever']
    if time_span not in time_spans:
        return HttpResponse('Invalid time span')
    try:
        stream = Stream.objects.get(pk=stream_id)
    except Stream.DoesNotExist:
        return HttpResponse('Invalid stream id')

    now = datetime.datetime(2012, 6, 6, 15, 15, 02)
    # now = datetime.datetime.now()
    if time_span == 'hour':
        min_time = now - datetime.timedelta(hours=1)
    elif time_span == 'day':
        min_time = now - datetime.timedelta(days=1)
    elif time_span == 'week':
        min_time = now - datetime.timedelta(days=7)
    elif time_span == 'month':
        min_time = now - datetime.timedelta(months=1)
    elif time_span == 'year':
        min_time = now - datetime.timedelta(years=1)
    elif time_span == 'forever':
        # there is no data from 2011 or before
        min_time = datetime.datetime(2012, 1, 1, 0, 0, 0)

    snum_dict = get_snum_dict(get_stream_numbers(stream, min_time))
    return HttpResponse(json.dumps(snum_dict))

