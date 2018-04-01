from django.urls import path, include
from rest_framework import routers
from . import views, viewsets

router = routers.SimpleRouter()
router.register('damage-types', viewsets.DamageTypeViewSet)
router.register('bike-racks', viewsets.BikeRackViewSet)
router.register('bikes', viewsets.BikeViewSet)
router.register('groups', viewsets.GroupsViewSet)
router.register('users', viewsets.UsersViewSet)
router.register('locks', viewsets.BikeLockViewSet)

userRouter = routers.SimpleRouter()
userRouter.register('rentals', viewsets.UserRentalsViewSet, base_name='user_rentals')

userUrls = [
	path('info/', views.user_info)
]
userUrls += userRouter.urls

urlpatterns = [
	path('can-checkout/', views.can_checkout),
	path('checkout/', views.checkout),
	path('checkin/', views.check_in),
	path('check-in/', views.check_in),
	path('report-damage/', views.report_damage),
	path('status/', views.get_status),
	path('user/', include(userUrls)),
]

urlpatterns += router.urls
