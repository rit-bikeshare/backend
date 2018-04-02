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
	path('info/', views.UserInfoView.as_view())
]
userUrls += userRouter.urls

urlpatterns = [
	path('can-checkout/', views.CheckoutView.as_view(dry_run=True)),
	path('checkout/', views.CheckoutView.as_view(dry_run=False)),
	path('checkin/', views.CheckInView.as_view()),
	path('check-in/', views.CheckInView.as_view()),
	path('report-damage/', views.ReportDamage.as_view()),
	path('status/', views.StatusView.as_view()),
	path('user/', include(userUrls)),
]

urlpatterns += router.urls
