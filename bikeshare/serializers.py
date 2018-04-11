from django.contrib.gis.geos import Point
from rest_framework import serializers

from . import models
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

class BikeRackSerializerBase(serializers.ModelSerializer):
	bike_count = serializers.SerializerMethodField()
	lat = serializers.FloatField(write_only=True)
	lon = serializers.FloatField(write_only=True)

	class Meta:
		model = models.BikeRack
		fields = ('bike_count','lat', 'lon', 'id')

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

class BikeSerializerBase(serializers.ModelSerializer):
	lat = serializers.FloatField(write_only=True)
	lon = serializers.FloatField(write_only=True)

	class Meta:
		model = models.Bike
		fields = ('lat', 'lon', 'id')		
	
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

class UserInfoSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		fields = ('last_login', 'username', 'first_name', 'last_name', 'groups')
