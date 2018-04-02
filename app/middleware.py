from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser

from constance import config

from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def get_user_jwt(request):
	"""
	Replacement for django session auth get_user & auth.get_user
	 JSON Web Token authentication. Inspects the token for the user_id,
	 attempts to get that user from the DB & assigns the user on the
	 request object. Otherwise it defaults to AnonymousUser.

	This will work with existing decorators like LoginRequired  ;)

	Returns: instance of user object or AnonymousUser object
	"""

	user = None
	try:
		user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
		if user_jwt is not None:
			# store the first part from the tuple (user, obj)
			user = user_jwt[0]
	except:
		pass

	return user or AnonymousUser()


class JWTAuthenticationMiddleware(object):
	""" Middleware for authenticating JSON Web Tokens in Authorize Header """
	def __init__(self, get_response):
		self.get_response = get_response
	
	def __call__(self, request):
		if getattr(request, 'user', AnonymousUser()).is_anonymous:
			request.user = SimpleLazyObject(lambda: get_user_jwt(request))
		return self.get_response(request)

from django.http import JsonResponse
from rest_framework import status

class MaintenanceInterceptorMiddleware():
	def __init__(self, get_response):
		self.get_response = get_response
	#enddef

	def __call__(self, request):
		return self.get_response(request)
	#enddef

	def process_view(self, request, view_func, view_args, view_kwargs):
		if not config.MAINTENANCE_MODE:
			return None
		if getattr(view_func, 'disable_maintenance_check', False):
			return None
		if request.user.is_staff:
			return None # staff can access

		resp = {'detail': config.MAINTENANCE_MESSAGE}

		return JsonResponse(resp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
#endclass
