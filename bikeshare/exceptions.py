from rest_framework import status
from rest_framework.exceptions import APIException

class AlreadyRentedException(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = 'This bike is already rented!'
	default_code = 'already_rented'

class NotRentedException(APIException):
	status_code = status.HTTP_409_CONFLICT
	default_detail = 'This bike is not rented!'
	default_code = 'not_rented'

class NotYourRentalException(APIException):
	status_code = status.HTTP_403_FORBIDDEN
	default_detail = "You don't have this bike rented!"
	default_code = 'not_your_rental'