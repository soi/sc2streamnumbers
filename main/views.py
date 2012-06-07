import json
import time
import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404

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
    except Stream.DoesNotExist:
        raise Http404
    return render_to_response('detail.html',
                              {'stream': stream},
                              context_instance=RequestContext(request))

def stream_numbers(request, stream_id, time_span):
    time_spans = ['hour', 'day', 'week', 'month', 'year', 'forever']
    if time_span not in time_spans:
        return HttpResponse('Invalid time span')
    try:
        stream = Stream.objects.get(pk=stream_id)
    except Stream.DoesNotExist:
        return HttpResponse('Invalid stream id')

    return_arr = []
    if time_span == 'hour':
        now = datetime.datetime(2012, 6, 6, 15, 15, 02)
        # now = datetime.datetime.now()
        hour_before_now = now - datetime.timedelta(hours=1)
        stream_numbers = StreamNumber.objects \
                            .filter(stream=stream,
                                    interval__date__gt=hour_before_now) \
                            .order_by('interval__date')
        for snum in stream_numbers:
            unix_time = int(snum.interval.date.strftime("%s"))
            return_arr.append({
                                'date': unix_time,
                                'number': snum.number
                              })
    return HttpResponse(json.dumps(return_arr))

