from django.urls import path, include
from rest_framework import routers
from . import views, viewsets

router = routers.SimpleRouter()
router.register('damage-types', viewsets.DamageTypeViewSet)
router.register('bike-racks', viewsets.BikeRackViewSet)
router.register('bikes', viewsets.BikeViewSet)

urlpatterns = [
	path('can-checkout/', views.CheckoutView.as_view(dry_run=True)),
	path('checkout/', views.CheckoutView.as_view(dry_run=False)),
	path('checkin/', views.CheckInView.as_view()),
	path('check-in/', views.CheckInView.as_view()),
	path('report-damage/', views.ReportDamage.as_view()),
	path('history/', views.RentalHistory.as_view()),
	path('rentals/', views.CurrentRentals.as_view()),
]

urlpatterns += router.urls
