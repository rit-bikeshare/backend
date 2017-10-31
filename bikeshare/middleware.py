from constance import config
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
		if request.user.is_staff: return None # staff can access
		if not config.MAINTENANCE_MODE: return None

		resp = {'detail': config.MAINTENANCE_MESSAGE}

		return JsonResponse(resp, status=status.HTTP_503_SERVICE_UNAVAILABLE)
#endclass
