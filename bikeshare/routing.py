from django.urls import path

from bikeshare.consumers import LockConsumer, RentalLockState

websocket_urlpatterns = [
	path('lock/register/<slug:id>', LockConsumer),
	path('lock-state/<slug:id>', RentalLockState)
]
