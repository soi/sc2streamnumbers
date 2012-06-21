import json
import time
import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.contrib.sites.models import Site

from streams.main.models import (Stream, Interval, StreamNumber,
    StreamNumberType, StreamType)

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def homepage(request):
    latest_interval = Interval.objects.order_by('-date')[0]
    current_site = Site.objects.get_current()
    stream_numbers= StreamNumber.objects.select_related() \
        .filter(stream_type__name='SC2') \
        .filter(interval=latest_interval) \
        .filter(stream_number_type__id=1) \
        .order_by('-number')[:12]
    return render_to_response('homepage.html',
                              {
                                'stream_numbers': stream_numbers,
                                'interval': latest_interval,
                                'current_site': current_site,
                              },
                              context_instance=RequestContext(request))

def search(request, query):
    from django.db import connection, transaction
    latest_interval = Interval.objects.order_by('-date')[0]

    cursor = connection.cursor()
    cursor.execute('SELECT s.name, s.id, sn.number FROM main_stream as s \
                    LEFT JOIN main_streamnumber as sn \
                    ON sn.stream_id = s.id and sn.interval_id = %s \
                    WHERE s.name ILIKE \'\%%s\%\' \
                    ORDER BY \
                        CASE WHEN sn.number IS NULL THEN -1 \
                        ELSE sn.number END DESC;'
                    [
                        latest_interval.id,
                        query
                    ]);
    return HttpResponse(json.dumps(dictfetchall(cursor))

def detail(request, stream_id):
    try:
        stream = Stream.objects.get(pk=stream_id)
        current_site = Site.objects.get_current()
    except Stream.DoesNotExist:
        raise Http404
    return render_to_response('detail.html',
                              {
                                'stream': stream,
                                'current_site': current_site,
                              },
                              context_instance=RequestContext(request))

def stream_numbers(request, stream_id, time_span, time_span_end='latest'):
    def get_stream_numbers(stream, min_time, max_time, snt_name):
        from django.db import connection, transaction

        cursor = connection.cursor()
        snt = StreamNumberType.objects.get(name=snt_name)
        cursor.execute('SELECT sn.number, i.date FROM main_interval as i \
                        LEFT JOIN main_streamnumber as sn \
                            ON (sn.interval_id = i.id \
                                AND sn.stream_id = %s  \
                                AND sn.stream_number_type_id = %s) \
                        WHERE i.date >= %s \
                            AND i.date <= %s \
                            AND i.stream_number_type_id >= %s \
                        ORDER BY i.date ASC',
                        [
                            stream.id,
                            snt.id,
                            min_time,
                            max_time,
                            snt.id,
                        ]);

        stream_numbers = dictfetchall(cursor)
        for elem in stream_numbers:
            elem['date'] = int(elem['date'].strftime("%s"))
        return stream_numbers

    # time_spans = ['hour', 'day', 'week', 'month', 'year', 'forever']
    time_spans = ['hour', 'day', 'week', 'month',]
    if time_span not in time_spans:
        return HttpResponse('Invalid time span')
    try:
        stream = Stream.objects.get(pk=stream_id)
    except Stream.DoesNotExist:
        return HttpResponse('Invalid stream id')

    if time_span_end == 'latest':
        max_time = datetime.datetime.now()
    else:
        max_time = datetime.datetime.fromtimestamp(int(time_span_end) + 1)

    if time_span == 'hour':
        min_time = max_time - datetime.timedelta(hours=1, minutes=5)
    elif time_span == 'day':
        min_time = max_time - datetime.timedelta(days=1, minutes=30)
    elif time_span == 'week':
        min_time = max_time - datetime.timedelta(days=7, hours=4)
    elif time_span == 'month':
        min_time = max_time - datetime.timedelta(days=30)

    return_data = get_stream_numbers(stream, min_time, max_time, time_span)
    return HttpResponse(json.dumps(return_data))
