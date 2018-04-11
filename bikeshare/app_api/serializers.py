from django.contrib.gis.geos import Point
from rest_framework import serializers

from bikeshare import models
from bikeshare.serializers import BikeRackSerializerBase, BikeSerializerBase
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

class BikeRackSerializer(BikeRackSerializerBase):
	pass

class BikeLockSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.BikeLock
		fields = '__all__'

class BikeSerializer(BikeSerializerBase):
	pass
		
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

class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = ('id', 'name')

class UserRentalSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Rental
		fields = ('renter', 'bike', 'rented_at')
