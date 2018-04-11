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
	class Meta:
		model = models.Bike
		exclude = ('location',)

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

class UsersSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		exclude = ('password','email','is_superuser', 'is_staff')

class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Permission
		exclude = ('content_type','codename')
