from rest_framework import status
from rest_framework.exceptions import APIException

class CheckoutDisabledException(APIException):
	status_code = status.HTTP_503_SERVICE_UNAVAILABLE
	default_detail = 'Bikes cannot be rented'
	default_code = 'checkout_disallowed'

	def __init__(self, message):
		self.detail = message

class AlreadyRentedException(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = 'This bike is already rented!'
	default_code = 'already_rented'

class BikeDamagedException(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = "This bike can't be rented because it's damaged."
	default_code = 'bike_damaged'

class BikeNotRentableException(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = "This bike cannot be rented at this time."
	default_code = 'bike_not_rentable'

class NotRentedException(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = 'This bike is not rented!'
	default_code = 'not_rented'

class NotYourRentalException(APIException):
	status_code = status.HTTP_403_FORBIDDEN
	default_detail = "You don't have this bike rented!"
	default_code = 'not_your_rental'

class DropAnywhereNotSupportedException(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = 'Drop anywhere is not supported.'
	default_code = 'drop_anywhere_disabled'

class DryRunSucceeded(APIException):
	status_code = status.HTTP_200_OK
	default_detail = 'Dry run succeeded'
	default_code = 'dry_run_succeeded'
