import decimal
from rest_framework import serializers

from . import models

class BikeRackSerializer(serializers.ModelSerializer):
	bike_count = serializers.SerializerMethodField()

	class Meta:
		model = models.BikeRack
		fields = '__all__'		

	def get_bike_count(self, obj):
		user = self.context['request'].user
		rentable_bikes = models.Bike.rentable_bikes(user)

		lat, lon = obj.lat, obj.lon

		tol = decimal.Decimal(.001)

		return rentable_bikes.filter(
			lat__gt=lat-tol,
			lat__lt=lat+tol,
			lon__lt=lon+tol,
			lon__gt=lon-tol
		).count()


class BikeSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Bike
		fields = '__all__'
		
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
	lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
	lon = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)

	def validate(self, data):
		# Ensure that if we got lat, we also got lon
		if ('lat' in data) != ('lon' in data): raise serializers.ValidationError('Both lat and lon must be specified')

		if not (('lat' in data) or ('bikerack' in data)): raise serializers.ValidationError('Must specify either bikerack or lat/lon')

		# If we got bikerack, it's an error to supply lat/lon
		if ('lat' in data) and ('bikerack' in data): raise serializers.ValidationError('Cannot specify both bikerack and lat/lon')

		# All good
		return data

class ReportDamageRequestSerializer(serializers.Serializer):
	bike = serializers.SlugField()
	damage_type = serializers.SlugField()
	comments = serializers.CharField()
	critical = serializers.BooleanField()
