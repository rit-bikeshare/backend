from django_shib_auth.core import ShibAuthCore, ShibSessionAuthCore
from rest_framework_jwt.settings import api_settings

from django.shortcuts import redirect
from django.views import View
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response

import urllib

class JwtLogoutView(ShibAuthCore, APIView):
	"""
	Defines a view that does nothing, since revoking the token is impossible
	"""
	def get(self, request, *args, **kwargs):
		return Response({
			'success': True
		})

class JwtLoginView(ShibAuthCore, APIView):
	"""
	Defines a view that will read shib headers and use them to create/log in a user.
	This MUST be protected by Shib or anyone could spoof anything.
	"""
	def get(self, request, *args, **kwargs):
		user = self.get_user(request)

		jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
		jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

		payload = jwt_payload_handler(user)
		token = jwt_encode_handler(payload)

		if request.GET.get('expo', 'false') == 'true':
			return redirect('https://auth.expo.io/@bikeshare/bikeshare?token=' + urllib.parse.quote_plus(token))
		if request.GET.get('admin-local', 'false') == 'true':
			return redirect('http://local.bikesharedev.rit.edu/admin/auth/success?token=' + urllib.parse.quote_plus(token))
		if request.GET.get('admin-qa', 'false') == 'true':
			return redirect('http://bikesharedev.rit.edu/admin/auth/success?token=' + urllib.parse.quote_plus(token))
		if request.GET.get('admin', 'false') == 'true':
			return redirect('/admin/auth/success?token=' + urllib.parse.quote_plus(token))
		
		return Response({
			'token': token
		})

class AdminLogin(ShibSessionAuthCore, View):
	"""
	Defines a view that persists Shib user data in the session
	and redirects to admin home.
	"""
	def get(self, request):
		print(request.user)
		self.login(request)

		return redirect(reverse('admin:index'))
