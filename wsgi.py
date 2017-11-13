"""
WSGI config for bikeshare project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application
import os

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
	from django.core.exceptions import ImproperlyConfigured
	raise ImproperlyConfigured('You must define the environment variable DJANGO_SETTINGS_MODULE.')

application = get_wsgi_application()
