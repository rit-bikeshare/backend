from functools import wraps

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from .app_settings import SHIB_ATTRIBUTE_MAP, SHIB_MOCK, SHIB_MOCK_ATTRIBUTES, SHIB_USERNAME_ATTRIB_NAME

def EnsureAuthMiddleware(request):
	# AuthenticationMiddleware is required so that request.user exists.
	if not hasattr(request, 'user'):
		raise ImproperlyConfigured(
			"The Shib auth functions requires the"
			" authentication middleware to be installed. Edit your"
			" MIDDLEWARE_CLASSES setting to insert"
			" 'django.contrib.auth.middleware.AuthenticationMiddleware'.")

class ShibAuthCore:
	def logout(self, request):
		EnsureAuthMiddleware(request)

		auth.logout(request)
		request.session.flush() # Force the session to be discarded

	def login(self, request):
		EnsureAuthMiddleware(request)

		username, shib_meta = self._fetch_headers(request)

		new_user = auth.authenticate(request, username=username, shib_meta=shib_meta)

		if not new_user:
			# No one found... oops
			self.logout() # Log out anyone currently logged in to prevent session stealing
			raise PermissionDenied("User does not exist")

		# Check if a different user is already logged in to this session
		# If so, log them out of our session
		if not request.user.is_anonymous and request.user.username != new_user.username: self.logout(request)

		# User is valid.  Set request.user and persist user in the session
		# by logging the user in.
		if request.user.is_anonymous: auth.login(request, new_user)

		# We now have a valid user instance
		# Update its attributes with our shib meta to capture
		# any values that aren't on our model
		request.user.__dict__.update(shib_meta)
		request.user.save()

	def _fetch_headers(self, request):
		# inject shib attributes
		if settings.DEBUG and SHIB_MOCK: request.META.update(SHIB_MOCK_ATTRIBUTES)

		username = request.META.get(SHIB_USERNAME_ATTRIB_NAME, None)
		# If we got None or an empty value, something went wrong.
		if not username: raise ImproperlyConfigured("Didn't get a shib username in the field called '{}'..."
			" Is this path protected by shib?".format(SHIB_USERNAME_ATTRIB_NAME))

		# Make sure we have all required Shibboleth elements before proceeding.
		shib_meta, missing = self.parse_attributes(request)
		request.session['shib'] = shib_meta

		if len(missing) != 0: raise ShibbolethValidationError("All required Shibboleth elements not found. Missing: %s" % missing)
		
		return username, shib_meta
	
	@staticmethod
	def parse_attributes(request):
		"""
		Parse the incoming Shibboleth attributes and convert them to the internal data structure.
		From: https://github.com/russell/django-shibboleth/blob/master/django_shibboleth/utils.py
		Pull the mapped attributes from the apache headers.
		"""
		shib_attrs = {}

		missing = []
		
		meta = request.META
		for header, attr in list(SHIB_ATTRIBUTE_MAP.items()):
			required, name = attr
			value = meta.get(header, None)
			if required and (not value or value == ''):
				missing.append(name)
			else:
				shib_attrs[name] = value

		return shib_attrs, missing