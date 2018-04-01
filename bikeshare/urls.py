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
	path('info/', views.UserInfoView)
]
userUrls += userRouter.urls

urlpatterns = [
	path('can-checkout/', views.CheckoutView(True).as_view()),
	path('checkout/', views.CheckoutView(False).as_view()),
	path('checkin/', views.CheckInView().as_view()),
	path('check-in/', views.CheckInView().as_view()),
	path('report-damage/', views.ReportDamage().as_view()),
	path('status/', views.StatusView().as_view()),
	path('user/', include(userUrls)),
]

urlpatterns += router.urls
