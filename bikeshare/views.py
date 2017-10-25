from django.contrib.auth.decorators import permission_required as __permission_required
from django.db import transaction
from django.db.models import Case, When, F
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework import permissions, status
from rest_framework.response import Response

from . import models, serializers

def permission_required(perm):
	return __permission_required(perm, raise_exception=True)

class AlreadyRentedException(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = 'This bike is already rented!'
	defult_code = 'already_rented'

@csrf_exempt
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@permission_required('bikeshare.rent_bike')
def checkout(request):
	serializer = serializers.CheckoutRequestSerializer(data=request.data)
	if not serializer.is_valid(): return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	# Get the bike
	bike = get_object_or_404(models.Bike, id=serializer.validated_data['bike'])

	# Make a new rental. For now the duration is hardcoded
	rental_start = models.Rental.get_rental_start()
	rental_end = models.Rental.get_rental_end(rental_start)

	rental = models.Rental(renter=request.user, bike=bike, rented_at=rental_start, should_return_at=rental_end)

	# Try to save it, failing if this bike is already rented
	# Start a new transaction
	with transaction.atomic():
		rental.save()
		# Now try to update the bike's rental, but only if it's not already rented.
		num_updated = models.Bike.objects.filter(id=bike.id, current_rental=None).update(current_rental=rental)

		if num_updated != 1:
			raise AlreadyRentedException()
	#end transaction

	return Response(serializers.RentalSerializer(rental).data, status=status.HTTP_201_CREATED)
#end checkout


