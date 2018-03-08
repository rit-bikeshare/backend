from django.contrib.auth import get_user_model
from django.contrib.auth.backends import RemoteUserBackend
from django.conf import settings

class ShibbolethBackend(RemoteUserBackend):
	def __init__(self, create_unknown_user = getattr(settings, 'CREATE_UNKNOWN_USER', True)):
		# Create a User object if not already in the database?
		self.create_unknown_user = create_unknown_user

	def authenticate(self, request, username=None, shib_meta=None):
		if username is None or shib_meta is None: return # This request is not meant for us

		username = self.clean_username(username)

		UserModel = get_user_model()
		usernameDict = { UserModel.USERNAME_FIELD: username }

		if self.create_unknown_user:
			model_field_names = [x.name for x in UserModel._meta.get_fields()]
			model_field_dict = dict([(x, shib_meta[x]) for x in shib_meta if x in model_field_names])
			user, created = UserModel.objects.get_or_create(**usernameDict, defaults=model_field_dict)
			if created: self.configure_user(user, shib_meta=shib_meta)
			user.save()
		else:
			try: user = User.objects.get(**usernameDict)
			except UserModel.DoesNotExist: return # Bail out if we can't find the user
		#endif

		# TODO: Update groups

		return user if self.user_can_authenticate(user) else None
	
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