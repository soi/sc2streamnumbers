import os
import sys

path = '/var/www/django'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'streams.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
