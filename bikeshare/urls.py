from django.conf.urls import url
from . import views

urlpatterns = [
	url('^checkout/$', views.checkout),
	url('^checkin/$', views.check_in),
	url('^report-damage/$', views.report_damage),
	url('^damage-types/list/$', views.DamageTypeList.as_view()),
	url('^bike-racks/list/$', views.BikeRackList.as_view()),
	url('^bikes/list/$', views.BikeList.as_view()),
	url('^status/$', views.get_status)
]
