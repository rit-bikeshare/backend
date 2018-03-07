from django.shortcuts import render
from django.views import View

from .core import ShibAuthCore

class LogoutView(ShibAuthCore, View):
	def get(self, request, *args, **kwargs):
		self.logout(request)

		return render(request, 'shib_auth/logged_out.html')


class LoginView(ShibAuthCore, View):
	"""
	Defines a view that will read shib headers and use them to create/log in a user.
	This MUST be protected by Shib or anyone could spoof anything.
	"""
	def get(self, request, *args, **kwargs):
		self.login(request)

		return render(request, 'shib_auth/login.html')
