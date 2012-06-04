from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404


from streams.main.models import Stream, Interval, StreamNumber

def homepage(request):
    return HttpResponse("Success")

