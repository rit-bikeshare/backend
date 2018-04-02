from functools import wraps

from constance import config
from django.db import transaction
from django.db.models import Case, When, F
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.views import APIView as __APIView
from rest_framework import status, generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from . import models, serializers, exceptions, permissions

class Useful404Mixin():
	"""
	Mixin to provide more useful 404 errors. rest framework
	subs in a very generic error message if it catches a 404
	"""
	
	def as_view(self, * args, ** kwargs):
		view_func = super().as_view( * args, ** kwargs)
		
		@wraps(view_func)
		def exception_translator(*f_args, **f_kwargs):
			try: return view_func(*f_args, **f_kwargs)
			except Http404 as e: raise NotFound(detail=str(e))

		return exception_translator	
#end class

class APIView(Useful404Mixin, __APIView):
	pass

class StatusView(APIView):
	def __init__(self, * args, ** kwargs):
		super().__init__( * args, ** kwargs)
		self.visible_settings = (
			'ALLOW_CHECKOUT',
			'CHECKOUT_DISALLOWED_MESSAGE',
			'MAINTENANCE_MODE',
			'MAINTENANCE_MESSAGE',
			'ENABLE_DROP_ANYWHERE'
		)

	def as_view(self, * args, ** kwargs):
		view = super().as_view(*args, ** kwargs)
		view.disable_maintenance_check = True
		return view

	def get(self, request):
		status = dict(map(lambda k: (k, getattr(config, k)), self.visible_settings))
		return Response(status)

class UserInfoView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	
	def get(self, request):
		return Response(serializers.UserInfoSerializer(request.user).data)

class CheckoutView(APIView):
	permission_classes = (permissions.IsAuthenticated, permissions.CanRentBike)

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

			if dry_run:
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
