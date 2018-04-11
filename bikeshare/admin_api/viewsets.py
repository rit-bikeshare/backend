"""
Standardized views provided by rest framework.
"""

from bikeshare import models
from . import serializers

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, mixins, pagination

class RestrictedViewDjangoModelPermissions(permissions.DjangoModelPermissions):
	 perms_map = {
		'GET': ['%(app_label)s.change_%(model_name)s'],
		'OPTIONS': [],
		'HEAD': ['%(app_label)s.change_%(model_name)s'],
		'POST': ['%(app_label)s.add_%(model_name)s'],
		'PUT': ['%(app_label)s.change_%(model_name)s'],
		'PATCH': ['%(app_label)s.change_%(model_name)s'],
		'DELETE': ['%(app_label)s.delete_%(model_name)s'],
	}

class DamageTypeViewSet(viewsets.ModelViewSet):
	queryset = models.DamageType.objects.all()
	serializer_class = serializers.DamageTypeSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)

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
	
