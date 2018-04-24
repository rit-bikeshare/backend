"""
Standardized views provided by rest framework.
"""

from bikeshare import models
from . import serializers
from .permissions import RestrictedViewDjangoModelPermissions

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, pagination

class DamageTypeViewSet(viewsets.ModelViewSet):
	queryset = models.DamageType.objects.all()
	serializer_class = serializers.DamageTypeSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)

class DamageReportViewSet(viewsets.ModelViewSet):
	queryset = models.DamageReport.objects.all()
	serializer_class = serializers.DamageReportSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)
	filter_fields = ('acknowledged', 'bike', 'critical', 'resolved_by')


class MaintenanceReportViewSet(viewsets.ModelViewSet):
	queryset = models.MaintenanceReport.objects.all()
	serializer_class = serializers.MaintenanceReportSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)
	filter_fields = ('bike',)	

class BikeRackViewSet(viewsets.ModelViewSet):
	queryset = models.BikeRack.objects.all()
	serializer_class = serializers.BikeRackSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)

class BikeLockViewSet(viewsets.ModelViewSet):
	queryset = models.BikeLock.objects.all()
	serializer_class = serializers.BikeLockSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)

class BikeViewSet(viewsets.ModelViewSet):
	queryset = models.Bike.objects.all()
	serializer_class = serializers.BikeSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)

class ActiveRentalsViewSet(viewsets.ModelViewSet):
	queryset = models.Rental.objects.filter(returned_at=None)
	serializer_class = serializers.RentalSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)

class RentalsViewSet(viewsets.ModelViewSet):
	queryset = models.Rental.objects.all()
	serializer_class = serializers.RentalSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)

	class Pagination(pagination.CursorPagination):
		ordering = ('-returned_at',)
		page_size = 50

	pagination_class = Pagination

class GroupViewSet(viewsets.ModelViewSet):
	serializer_class = serializers.GroupSerializer
	queryset = Group.objects.all()
	permission_classes = (RestrictedViewDjangoModelPermissions,)
	
class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = serializers.PermissionSerializer
	queryset = Permission.objects.all()
	permission_classes = (RestrictedViewDjangoModelPermissions,)	

class UsersViewSet(viewsets.ModelViewSet):
	serializer_class = serializers.UsersSerializer
	queryset = get_user_model().objects.all()
	permission_classes = (RestrictedViewDjangoModelPermissions,)
	filter_fields = ('first_name', 'last_name')
	
