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
