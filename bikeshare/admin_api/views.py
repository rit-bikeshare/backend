from bikeshare.views import APIView
from bikeshare import models

from constance import config, settings
from rest_framework import status, generics, pagination, permissions
from rest_framework.response import Response

from django.contrib.auth import get_user_model

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
		
		return Response(cfg)

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