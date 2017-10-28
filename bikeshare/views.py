from django.contrib.auth.decorators import permission_required as __permission_required
from django.db import transaction
from django.db.models import Case, When, F
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response

from . import models, serializers, exceptions

def permission_required(perm):
	return __permission_required(perm, raise_exception=True)


@csrf_exempt
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@permission_required('bikeshare.rent_bike')
def checkout(request):
	serializer = serializers.CheckoutRequestSerializer(data=request.data)
	if not serializer.is_valid(): return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	# Start a new transaction
	with transaction.atomic():
		# Get the bike with select_for_update to lock it for the duration of the transaction
		bike = get_object_or_404(models.Bike.objects.select_for_update(), id=serializer.validated_data['bike'])

		# Can't rent a bike twice
		if bike.current_rental is not None: raise exceptions.AlreadyRentedException()

		if not bike.visible and not request.user.has_perm('bikeshare.rent_hidden_bike'): raise exceptions.BikeNotRentableException()

		# Check for unresolved damage
		if models.DamageReport.objects.filter(bike=bike, resolved_by=None).exists(): raise exceptions.BikeDamagedException()

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
		lat, lon = get_object_or_404(models.BikeRack.objects.values_list('lat', 'lon'), id=bikerack_id)
	else:
		# Gave us coords directly
		lat, lon = serializer.validated_data['lat'], serializer.validated_data['lon']
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
		bike.lat, bike.lon = lat, lon
		bike.save()
	#end transaction

	return Response(serializers.RentalSerializer(rental).data, status=status.HTTP_200_OK)
#end checkin	
