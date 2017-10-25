from rest_framework import serializers

from . import models

class BikeSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Bike

class RentalSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Rental
		fields = '__all__'

class CheckoutRequestSerializer(serializers.Serializer):
	bike = serializers.SlugField()
