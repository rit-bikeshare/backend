from django.conf.urls import url, include
from rest_framework import routers
from . import views, viewsets

router = routers.SimpleRouter()
router.register(r'damage-types', viewsets.DamageTypeViewSet)
router.register(r'bike-racks', viewsets.BikeRackViewSet)
router.register(r'bikes', viewsets.BikeViewSet)
router.register(r'groups', viewsets.GroupsViewSet)
router.register(r'users', viewsets.UsersViewSet)

userRouter = routers.SimpleRouter()
userRouter.register('rentals', viewsets.UserRentalsViewSet, base_name='user_rentals')

userUrls = [
	url('^info/$', views.user_info)
]
userUrls += userRouter.urls

urlpatterns = [
	url('^can-checkout/$', views.can_checkout),
	url('^checkout/$', views.checkout),
	url('^checkin/$', views.check_in),
	url('^report-damage/$', views.report_damage),
	url('^status/$', views.get_status),
	url('^user/', include(userUrls)),
]

urlpatterns += router.urls
