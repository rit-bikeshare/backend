from django.contrib.gis.geos import Point
from rest_framework import serializers

from . import models
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

class UserInfoSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		fields = ('last_login', 'username', 'first_name', 'last_name', 'groups')

class BikeRackSerializer(serializers.ModelSerializer):
	bike_count = serializers.SerializerMethodField()
	lat = serializers.FloatField(write_only=True)
	lon = serializers.FloatField(write_only=True)

	class Meta:
		model = models.BikeRack
		exclude = ('location',)

	def get_lat(self, obj): return obj.location.y
	def get_lon(self, obj): return obj.location.x

	def get_bike_count(self, obj):
		user = self.context['request'].user
		rentable_bikes = models.Bike.rentable_bikes(user)
		return rentable_bikes.filter(
			location__within=obj.check_in_area
		).count()

	def to_representation(self, obj):
		ret = super().to_representation(obj)
		ret['lat'] = obj.location.y
		ret['lon'] = obj.location.x
		return ret

	def to_internal_value(self, data):
		ret = super().to_internal_value(data)
		ret['location'] = Point(ret['lon'], ret['lat'], srid=4326)
		del ret['lon']
		del ret['lat']
		return ret
		

class BikeLockSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.BikeLock
		fields = '__all__'

class BikeSerializer(serializers.ModelSerializer):
	lat = serializers.FloatField(write_only=True)
	lon = serializers.FloatField(write_only=True)
	lock = BikeLockSerializer(read_only=True)

	class Meta:
		model = models.Bike
		exclude = ('location',)
	
	def get_lat(self, obj): return obj.location.y
	def get_lon(self, obj): return obj.location.x

	def to_representation(self, obj):
		ret = super().to_representation(obj)
		ret['lat'] = obj.location.y
		ret['lon'] = obj.location.x
		return ret

	def to_internal_value(self, data):
		ret = super().to_internal_value(data)
		ret['location'] = Point(ret['lon'], ret['lat'], srid=4326)
		del ret['lon']
		del ret['lat']
		return ret
		
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

class CheckoutRequestSerializer(serializers.Serializer):
	bike = serializers.SlugField()

class CheckInRequestSerializer(serializers.Serializer):
	bike = serializers.SlugField()

	# Can specify bikerack OR lat/lon
	bikerack = serializers.SlugField(required=False)
	lat = serializers.FloatField(required=False)
	lon = serializers.FloatField(required=False)

	def validate(self, data):
		# Ensure that if we got lat, we also got lon
		if ('lat' in data) != ('lon' in data): raise serializers.ValidationError('Both lat and lon must be specified')

		if not (('lat' in data) or ('bikerack' in data)): raise serializers.ValidationError('Must specify either bikerack or lat/lon')

		# If we got bikerack, it's an error to supply lat/lon
		if ('lat' in data) and ('bikerack' in data): raise serializers.ValidationError('Cannot specify both bikerack and lat/lon')

		if 'lat' in data:
			data['location'] = Point(data['lon'], data['lat'], srid=4326)

		# All good
		return data

class ReportDamageRequestSerializer(serializers.Serializer):
	bike = serializers.SlugField()
	damage_type = serializers.SlugField()
	comments = serializers.CharField()
	critical = serializers.BooleanField()

class UsersSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		fields = ('id', 'last_login', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'groups')

class GroupSerializer(serializers.ModelSerializer):
	permissions = serializers.SerializerMethodField()

	class Meta:
		model = Group
		fields = '__all__'
	
	def get_permissions(self, obj):
		return obj.permissions.values_list('name', flat=True)
