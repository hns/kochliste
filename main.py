# Google App Engine imports.
import logging, os
from google.appengine.ext.webapp import util

# Must set this env var before importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# from django.core.management import setup_environ
# import settings

# setup_environ(settings)

# Force Django to reload its settings.
from django.conf import settings
settings._target = None

import django.core.handlers.wsgi
import django.core.signals
import django.db
import django.dispatch.dispatcher

# import locale
# locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

def log_exception(*args, **kwds):
  logging.exception('Exception in request:')

def main():
  # Create a Django application for WSGI.
  application = django.core.handlers.wsgi.WSGIHandler()

  # Run the WSGI CGI handler with that application.
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()

