from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404

from streams.main.models import Stream, Interval, StreamNumber

def homepage(request):
    latest_interval = Interval.objects.order_by('-date')[0]
    stream_nums= StreamNumber.objects.select_related() \
        .filter(interval=latest_interval).order_by('-number')

    return render_to_response('homepage.html',
                              {
                                'stream_numbers': stream_nums,
                                'interval': latest_interval
                              },
                              context_instance=RequestContext(request))
