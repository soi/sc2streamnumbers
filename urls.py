import os
from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'streams.views.home', name='home'),
    # url(r'^streams/', include('streams.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'streams.main.views.homepage'),
    url(r'^about/$', 'streams.main.views.about'),
    url(r'^search/(?P<query>\w+)/$', 'streams.main.views.search'),
    url(r'^(?P<stream_id>\d+)/$', 'streams.main.views.detail'),
    url(r'^(?P<stream_id>\d+)/(?P<time_span>\w+)/$', 'streams.main.views.stream_numbers'),
    url(r'^(?P<stream_id>\d+)/(?P<time_span>\w+)/(?P<time_span_end>\d+)/$', 'streams.main.views.stream_numbers'),

    # for the static stuff
    (
        r'^css/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': ''.join([os.path.dirname(__file__), '/static/css/'])}
    ),
    (
        r'^js/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': ''.join([os.path.dirname(__file__), '/static/js/'])}
    ),
    (
        r'^images/(?P<path>.*)$',
        'django.views.static.serve',
        {'document_root': ''.join([os.path.dirname(__file__), '/static/images/'])}
    ),
)
