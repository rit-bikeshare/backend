from functools import wraps

from bikeshare.views import APIView
from bikeshare import models

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from constance import config
from django.db import transaction
from django.db.models import Case, When, F
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import status, generics, pagination
from rest_framework.response import Response

from . import serializers, exceptions, permissions

class CheckoutView(APIView):
	permission_classes = (permissions.IsAuthenticated, permissions.CanRentBike)
	dry_run = None # Otherwise as_view complains

	class DryRunSucceeded(Exception):
		pass

	def __init__(self, dry_run, * args, ** kwargs):
		super().__init__( * args, ** kwargs)
		self.dry_run = dry_run

	def post(self, request):
		try:
			rental = self.check_out(request)			
		except CheckoutView.DryRunSucceeded:
			return Response({'success': True})

		return Response(serializers.RentalSerializer(rental).data, status=status.HTTP_201_CREATED)
	
	def check_out(self, request):
		if not config.ALLOW_CHECKOUT:
			raise exceptions.CheckoutDisabledException(config.CHECKOUT_DISALLOWED_MESSAGE)

		serializer = serializers.CheckoutRequestSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		# Start a new transaction
		with transaction.atomic():
			# Get the bike with select_for_update to lock it for the duration of the transaction
			bike = get_object_or_404(models.Bike.objects.select_for_update(), id=serializer.validated_data['bike'])

			# Can't rent a bike twice
			if bike.current_rental is not None:
				raise exceptions.AlreadyRentedException()

			if not bike.visible and not request.user.has_perm('bikeshare.rent_hidden_bike'):
				raise exceptions.BikeNotRentableException()

			# Check for unresolved critical damage
			if models.DamageReport.objects.filter(
				bike=bike,
				resolved_by=None,
				critical=True
			).exists():
				raise exceptions.BikeDamagedException()

			rental = models.Rental.objects.create(renter=request.user, bike=bike)

			bike.current_rental = rental
			bike.save()

			if self.dry_run:
				raise CheckoutView.DryRunSucceeded()
		#end transaction

		return rental

class CheckInView(APIView):
	# Not requiring bike.checkout perms here otherwise a user could get stuck with a checked out bike forever
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request):
		serializer = serializers.CheckInRequestSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		bikerack_id = serializer.validated_data.get('bikerack', None)
		if bikerack_id:
			# They gave us a bikerack, so look up its coords
			location = get_object_or_404(models.BikeRack.objects.values_list('location'), id=bikerack_id)[0]
		else:
			# Gave us coords directly
			if not config.ENABLE_DROP_ANYWHERE:
				raise exceptions.DropAnywhereNotSupportedException()
			location = serializer.validated_data['location']
		#endif

		with transaction.atomic():
			# Load the bike (if present)
			bike = get_object_or_404(models.Bike.objects.select_for_update(), id=serializer.validated_data['bike'])
			rental = bike.current_rental

			if rental is None:
				raise exceptions.NotRentedException()
			if rental.renter != request.user:
				raise exceptions.NotYourRentalException()

			# Set the rental's actual end to now
			rental.returned_at = timezone.now()
			rental.save()

			# clear the rental and update coords
			bike.previous_rental = rental
			bike.current_rental = None
			bike.location = location
			bike.save()
		#end transaction

		return Response(serializers.RentalSerializer(rental).data)
	#end check_in	

class ReportDamage(APIView):
	permission_classes = (permissions.IsAuthenticated, permissions.CanReportDamage)

	def post(self, request):
		serializer = serializers.ReportDamageRequestSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		# Load the bike (if present)
		bike = get_object_or_404(models.Bike, id=serializer.validated_data['bike'])
		damage_type = get_object_or_404(models.DamageType, id=serializer.validated_data['damage_type'])

		damage_report = models.DamageReport.objects.create(
			reporter=request.user,
			bike=bike,
			damage_type=damage_type,
			comments=serializer.validated_data['comments'],
			critical=(serializer.validated_data['critical'] or damage_type.force_critical)
		)

		return Response(serializers.DamageReportSerializer(damage_report).data)
#end report_damage

class CurrentRentals(generics.ListAPIView):
	serializer_class = serializers.RentalSerializer

	def get_queryset(self):
		return models.Rental.objects.filter(
			renter = self.request.user,
			returned_at=None
		)

class RentalHistory(generics.ListAPIView):
	class Pagination(pagination.PageNumberPagination):
		page_size = 100
	permission_classes = (permissions.IsAuthenticated,)
	pagination_class = Pagination
	serializer_class = serializers.RentalSerializer

	def get_queryset(self):
		return models.Rental.objects.filter(
			renter = self.request.user
		).order_by('-rented_at')

class LockControlView(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request):
		serializer = serializers.LockControlSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		bike = get_object_or_404(models.Bike, id=serializer.validated_data['bike'])
		if not bike.current_rental or bike.current_rental.renter != request.user:
			raise exceptions.NotYourRentalException()

		channel_layer = get_channel_layer()

		command = serializer.validated_data['command']

		payload = {
			"type": 'lock.control',
			"command": command
		}

		async_to_sync(channel_layer.send)(bike.lock.channel_name, payload)

		return Response({'success': True})

		
