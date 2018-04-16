from django.urls import path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import bikeshare.routing

websocket_urlpatterns = [
	path('', URLRouter(bikeshare.routing.websocket_urlpatterns))
]
