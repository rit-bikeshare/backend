from bikeshare.views import APIView
from bikeshare import models

from constance import config, settings
from rest_framework import status, generics, pagination, permissions
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from . import serializers
from .permissions import RestrictedViewDjangoModelPermissions

class DamagedBikes(generics.ListAPIView):
	queryset = models.Bike.damaged_bikes()
	serializer_class = serializers.BikeSerializer
	permission_classes = (RestrictedViewDjangoModelPermissions,)

class Settings(APIView):
	permission_classes = (permissions.IsAdminUser,)

	def get(self, request):
		cfg = []
		for name in settings.CONFIG:
			cfg.append({
				'name': name,
				'help': settings.CONFIG[name][1],
				'value': getattr(config, name)
			})
		
		return Response({
			'settings': cfg,
			'fieldsets': settings.CONFIG_FIELDSETS
		})

	def post(self, request):
		for k, v in request.data.items():
			k = k.upper()
			if k in settings.CONFIG:
				setattr(config, k, v)
		
		return self.get(request)


class Stats(APIView):
	permission_classes = (permissions.IsAdminUser,)
	def get(self, request):
		stats = [
			{'title': 'Active Rentals', 'value': models.Rental.objects.filter(returned_at=None).count()},
			{'title': 'Total Rentals', 'value': models.Rental.objects.count()},
			{'title': 'Total Riders', 'value': get_user_model().objects.count()},
			{'title': 'Total Bikes', 'value': models.Bike.objects.count()},
		]

		return Response(stats)

class LockControlView(APIView):
	permission_classes = (permissions.IsAdminUser,)

	def post(self, request):
		serializer = serializers.LockControlSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		bike = get_object_or_404(models.Bike, id=serializer.validated_data['bike'])

		channel_layer = get_channel_layer()

		command = serializer.validated_data['command']

		payload = {
			"type": 'lock.control',
			"command": command
		}

		if not bike.lock or bike.lock.channel_name == '':
			return Response({'error': 'Lock not properly configured.'}, status=500)

		async_to_sync(channel_layer.send)(bike.lock.channel_name, payload)

		return Response()