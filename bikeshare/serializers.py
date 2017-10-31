from rest_framework import serializers

from . import models

class BikeRackSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.BikeRack
		fields = '__all__'		

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
