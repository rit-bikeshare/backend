from django.urls import include

from channels.routing import ProtocolTypeRouter, URLRouter
import app.routing

import os

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
	from django.core.exceptions import ImproperlyConfigured
	raise ImproperlyConfigured('You must define the environment variable DJANGO_SETTINGS_MODULE.')

application = ProtocolTypeRouter({
	# (http->django views is added by default)
	'websocket': URLRouter(app.routing.websocket_urlpatterns),
})
