from rest_framework import routers
from . import viewsets, views
from django.urls import path


router = routers.SimpleRouter()
router.register('damage-types', viewsets.DamageTypeViewSet)
router.register('bike-racks', viewsets.BikeRackViewSet)
router.register('bikes', viewsets.BikeViewSet)
router.register('groups', viewsets.GroupViewSet)
router.register('permission', viewsets.PermissionViewSet)
router.register('users', viewsets.UsersViewSet)
router.register('locks', viewsets.BikeLockViewSet)
router.register('rentals', viewsets.RentalsViewSet)
router.register('active-rentals', viewsets.ActiveRentalsViewSet)
router.register('damage-reports', viewsets.DamageReportViewSet)
router.register('maintenance-reports', viewsets.MaintenanceReportViewSet)

urlpatterns = router.urls
urlpatterns += [
	path('damaged-bikes/', views.DamagedBikes.as_view()),
	path('stats/', views.Stats.as_view()),
	path('settings/', views.Settings.as_view())
]
