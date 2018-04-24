from bikeshare.views import APIView
from bikeshare import models

from rest_framework import status, generics, pagination
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from . import serializers, permissions

class DamagedBikes(generics.ListAPIView):
	queryset = models.Bike.damaged_bikes()
	serializer_class = serializers.BikeSerializer
	permission_classes = (permissions.RestrictedViewDjangoModelPermissions,)

class Stats(APIView):
	def get(self, request):
		stats = [
			{'title': 'Active Rentals', 'value': models.Rental.objects.filter(returned_at=None).count()},
			{'title': 'Total Rentals', 'value': models.Rental.objects.count()},
			{'title': 'Total Riders', 'value': get_user_model().objects.count()},
			{'title': 'Total Bikes', 'value': models.Bike.objects.count()},
		]

		return Response(stats)