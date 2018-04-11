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

class BikeLockViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.BikeLock.objects.all()
	serializer_class = serializers.BikeLockSerializer
	permission_classes = (permissions.DjangoModelPermissions,)

class BikeViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.Bike.objects.none()
	serializer_class = serializers.BikeSerializer
	permission_classes = (permissions.DjangoModelPermissions,)

	def get_queryset(self):
		query = models.Bike.objects.filter(current_rental=None)

		if not self.request.user.has_perm('bikeshare.rent_hidden_bike'):
			query = query.filter(visible=True)

		damaged_bikes = models.DamageReport.objects.filter(
			resolved_by=None,
			critical=True
		).values('id')

		query = query.exclude(id__in=damaged_bikes)

		return query


class UserRentalsViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = serializers.UserRentalSerializer
	permission_classes = (permissions.DjangoModelPermissions,)

	def get_queryset(self):
		return models.Rental.objects.filter(
			renter=self.request.user,
			returned_at=None
		)

class GroupsViewSet(viewsets.ReadOnlyModelViewSet):
	serializer_class = serializers.GroupSerializer
	queryset = Group.objects.all()
