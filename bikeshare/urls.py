from django.conf.urls import url
from . import views

urlpatterns = [
	url('^checkout/$', views.checkout),
	url('^checkin/$', views.check_in),
]
