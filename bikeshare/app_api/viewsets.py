"""
Standardized views provided by rest framework.
"""

from bikeshare import models
from . import serializers

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, mixins, pagination

class DamageTypeViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.DamageType.objects.all()
	serializer_class = serializers.DamageTypeSerializer
	permission_classes = (permissions.DjangoModelPermissions,)

class BikeRackViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.BikeRack.objects.all()
	serializer_class = serializers.BikeRackSerializer
	permission_classes = (permissions.DjangoModelPermissions,)

class BikeViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.Bike.objects.none()
	serializer_class = serializers.BikeSerializer
	permission_classes = (permissions.DjangoModelPermissions,)

	def get_queryset(self):
		return models.Bike.rentable_bikes(self.request.user)

class GroupsViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = serializers.GroupSerializer
	queryset = Group.objects.all()
