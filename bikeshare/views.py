from constance import config
from django.contrib.auth.decorators import permission_required as __permission_required
from django.db import transaction
from django.db.models import Case, When, F
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.decorators import api_view as __api_view, permission_classes
from rest_framework import permissions, status, generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from . import models, serializers, exceptions

def permission_required(perm):
	return __permission_required(perm, raise_exception=True)

def api_view(*args, **kwargs):
	"""
	Wrapper to provide more useful 404 errors. rest framework
	subs in a very generic error message if it catches a 404
	"""
	api_wrapper_func = __api_view(*args, **kwargs)

	def wrapper(func):
		def exception_translator(*f_args, **f_kwargs):
			try: return func(*f_args, **f_kwargs)
			except Http404 as e: raise NotFound(detail=str(e))

		return api_wrapper_func(exception_translator)
	#end wrapper

	return wrapper

class DamageTypeList(generics.ListAPIView):
	queryset = models.DamageType.objects.all()
	serializer_class = serializers.DamageTypeSerializer

class BikeRackList(generics.ListAPIView):
	queryset = models.BikeRack.objects.all()
	serializer_class = serializers.BikeRackSerializer

class BikeList(generics.ListAPIView):
	queryset = models.Bike.objects.all()
	serializer_class = serializers.BikeSerializer

@csrf_exempt
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@permission_required('bikeshare.rent_bike')
def checkout(request):
	if not config.ALLOW_CHECKOUT: raise exceptions.CheckoutDisabledException(config.CHECKOUT_DISALLOWED_MESSAGE)

	serializer = serializers.CheckoutRequestSerializer(data=request.data)
	if not serializer.is_valid(): return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	# Start a new transaction
	with transaction.atomic():
		# Get the bike with select_for_update to lock it for the duration of the transaction
		bike = get_object_or_404(models.Bike.objects.select_for_update(), id=serializer.validated_data['bike'])

		# Can't rent a bike twice
		if bike.current_rental is not None: raise exceptions.AlreadyRentedException()

		if not bike.visible and not request.user.has_perm('bikeshare.rent_hidden_bike'): raise exceptions.BikeNotRentableException()

		# Check for unresolved critical damage
		if models.DamageReport.objects.filter(
			bike=bike,
			resolved_by=None,
			critical=True
		).exists(): raise exceptions.BikeDamagedException()

		# Make a new rental. For now the duration is hardcoded
		rental_start = models.Rental.get_rental_start()
		rental_end = models.Rental.get_rental_end(rental_start)

		rental = models.Rental.objects.create(renter=request.user, bike=bike, rented_at=rental_start, should_return_at=rental_end)

		bike.current_rental = rental
		bike.save()
	#end transaction

	return Response(serializers.RentalSerializer(rental).data, status=status.HTTP_201_CREATED)
#end checkout

@csrf_exempt
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
# Not requiring bike.checkout perms here otherwise a user could get stuck with a checked out bike forever
def check_in(request):
	serializer = serializers.CheckInRequestSerializer(data=request.data)
	if not serializer.is_valid(): return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	bikerack_id = serializer.validated_data.get('bikerack', None)
	if bikerack_id:
		# They gave us a bikerack, so look up its coords
		location = get_object_or_404(models.BikeRack.objects.values_list('location'), id=bikerack_id)
	else:
		# Gave us coords directly
		location = serializer.validated_data['location']
	#endif

	with transaction.atomic():
		# Load the bike (if present)
		bike = get_object_or_404(models.Bike.objects.select_for_update(), id=serializer.validated_data['bike'])
		rental = bike.current_rental

		if rental is None: raise exceptions.NotRentedException()
		if rental.renter != request.user: raise exceptions.NotYourRentalException()

		# Set the rental's actual end to now
		rental.returned_at = timezone.now()
		rental.save()

		# clear the rental and update coords
		bike.current_rental = None
		bike.location = location
		bike.save()
	#end transaction

	return Response(serializers.RentalSerializer(rental).data, status=status.HTTP_200_OK)
#end checkin	

@csrf_exempt
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@permission_required('bikeshare.report_damage')
def report_damage(request):
	serializer = serializers.ReportDamageRequestSerializer(data=request.data)
	if not serializer.is_valid(): return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

	return Response(serializers.DamageReportSerializer(damage_report).data, status=status.HTTP_200_OK)
#end report_damage	
	