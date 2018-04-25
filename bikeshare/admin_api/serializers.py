from django.contrib.gis.geos import Point
from rest_framework import serializers

from bikeshare import models
from bikeshare.serializers import BikeRackSerializerBase, BikeSerializerBase
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

class BikeRackSerializer(BikeRackSerializerBase):
	class Meta:
		model = models.BikeRack
		exclude = ('location',)

class BikeLockSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.BikeLock
		fields = '__all__'

class BikeSerializer(BikeSerializerBase):
	current_renter_username = serializers.SerializerMethodField()
	previous_renter_username = serializers.SerializerMethodField()

	class Meta:
		model = models.Bike
		exclude = ('location',)

	def get_current_renter_username(self, obj):
		if not obj.current_rental:
			return None
		return obj.current_rental.renter.username

	def get_previous_renter_username(self, obj):
		if not obj.previous_rental:
			return None
		return obj.previous_rental.renter.username

class RentalSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Rental
		fields = '__all__'

class DamageReportSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.DamageReport
		fields = '__all__'

class DamageTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.DamageType
		fields = '__all__'

class MaintenanceReportSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.MaintenanceReport
		fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		exclude = ('password','email','is_superuser')

class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Permission
		exclude = ('content_type','codename')

class LockControlSerializer(serializers.Serializer):
	bike = serializers.SlugField()
	command = serializers.ChoiceField(['lock', 'unlock'])