from rest_framework import routers
from . import viewsets

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
