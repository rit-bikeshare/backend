from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import render
from django.views import View

from .app_settings import SHIB_ATTRIBUTE_MAP, SHIB_MOCK, SHIB_MOCK_ATTRIBUTES, SHIB_USERNAME_ATTRIB_NAME

def _logout(request):
	auth.logout(request)
	request.session.flush() # Force the session to be discarded

class EnsureAuthenticationMixin:
	def get(self, request, *args, **kwargs):
		# AuthenticationMiddleware is required so that request.user exists.
		if not hasattr(request, 'user'):
			raise ImproperlyConfigured(
				"The Shib auth functions requires the"
				" authentication middleware to be installed. Edit your"
				" MIDDLEWARE_CLASSES setting to insert"
				" 'django.contrib.auth.middleware.AuthenticationMiddleware'.")
		return super().get(self, request, *args, **kwargs)       


class LogoutView(EnsureAuthenticationMixin, View):
	def get(self, request, *args, **kwargs):
		_logout(request)

		return render(request, 'shib_auth/logged_out.html')


class LoginView(EnsureAuthenticationMixin, View):
	"""
	Defines a view that will read shib headers and use them to create/log in a user.
	This MUST be protected by Shib or anyone could spoof anything.
	"""
	def __init__(self, create_unknown_user = getattr(settings, 'CREATE_UNKNOWN_USER', True)):
		# Create a User object if not already in the database?
		self.create_unknown_user = create_unknown_user

	def get(self, request, *args, **kwargs):
		# inject shib attributes
		if settings.DEBUG and SHIB_MOCK: request.META.update(SHIB_MOCK_ATTRIBUTES)

		username = self.clean_username(request.META.get(SHIB_USERNAME_ATTRIB_NAME, None), request)
		# If we got None or an empty value, something went wrong.
		if not username: raise ImproperlyConfigured("Didn't get a shib username in the field called '{}'..."
			" Is this path protected by shib?".format(SHIB_USERNAME_ATTRIB_NAME))

		# Check if a different user is already logged in to this session
		# If so, log them out of our session
		if not request.user.is_anonymous and request.user.username != username: _logout(request)

		# Make sure we have all required Shibboleth elements before proceeding.
		shib_meta, missing = self.parse_attributes(request)
		request.session['shib'] = shib_meta

		if len(missing) != 0: raise ShibbolethValidationError("All required Shibboleth elements not found. Missing: %s" % missing)
		
		# Now we're ready to actually authenticate the user
		UserModel = auth.get_user_model()
		usernameDict = { UserModel.USERNAME_FIELD: username }

		if self.create_unknown_user:
			model_field_names = [x.name for x in UserModel._meta.get_fields()]
			model_field_dict = dict([(x, shib_meta[x]) for x in shib_meta if x in model_field_names])
			user, created = UserModel.objects.get_or_create(**usernameDict, defaults=kwargs)
			if created: self.configure_user(user, extra=kwargs)
		else:
			try: user = User.objects.get(**usernameDict)
			except UserModel.DoesNotExist: raise PermissionDenied("User '{}' not found".format(username)) # Bail out if we can't find the user
		#endif

		# We now have a valid user instance
		# Update its attributes with our shib meta to capture
		# any values that aren't on our model
		request.user.__dict__.update(shib_meta)
		user.save()

		if not self.user_can_authenticate(user): return PermissionDenied("You're not allowed to log in")

		# User is valid.  Set request.user and persist user in the session
		# by logging the user in.
		auth.login(request, user)

		return render(request, 'shib_auth/login.html')

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

	def clean_username(self, username, request=None): return username
	
	def update_shib_params(self, user, params): pass

	def configure_user(self, user, extra):
		user.set_unusable_password()

	def user_can_authenticate(self, user):
		"""
		Reject users with is_active=False. Custom user models that don't have
		that attribute are allowed.
		This is already provided in Django 1.10+ - included here to support
		lower versions
		"""
		is_active = getattr(user, 'is_active', None)
		return is_active or is_active is None

class ShibbolethValidationError(Exception):
	pass
