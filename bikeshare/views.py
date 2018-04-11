from functools import wraps

from constance import config
from django.db import transaction
from django.db.models import Case, When, F
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.views import APIView as __APIView
from rest_framework import status, generics, pagination, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from . import models, serializers

class Useful404Mixin():
	"""
	Mixin to provide more useful 404 errors. rest framework
	subs in a very generic error message if it catches a 404
	"""

	def __init__(self, * args, ** kwargs):
		super().__init__(*args, **kwargs)
	
	@classmethod
	def as_view(cls, ** kwargs):
		view_func = super().as_view(** kwargs)
		
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

	@classmethod
	def as_view(cls, ** kwargs):
		view = super().as_view(** kwargs)
		view.disable_maintenance_check = True
		return view

	def get(self, request):
		status = dict(map(lambda k: (k, getattr(config, k)), self.visible_settings))
		return Response(status)

class UserInfoView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	
	def get(self, request):
		return Response(serializers.UserInfoSerializer(request.user).data)
