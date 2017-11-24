from django.contrib.auth import get_user_model
from django.contrib.auth.backends import RemoteUserBackend
from django.conf import settings


class ShibbolethRemoteUserBackend(RemoteUserBackend):
	# Create a User object if not already in the database?
	create_unknown_user = getattr(settings, 'CREATE_UNKNOWN_USER', True)

	def authenticate(self, request, remote_user, **kwargs):
		if not remote_user: return

		UserModel = get_user_model()
		usernameDict = { UserModel.USERNAME_FIELD: self.clean_username(remote_user) }

		model_field_names = [x.name for x in UserModel._meta.get_fields()]
		model_field_dict = dict([(x, kwargs[x]) for x in kwargs if x in model_field_names])

		if self.create_unknown_user:
			user, created = UserModel.objects.get_or_create(**usernameDict, defaults=kwargs)
			if created: self.configure_user(user, extra=kwargs)
		else:
			try: user = User.objects.get(**usernameDict)
			except UserModel.DoesNotExist: return # Bail out if we can't find the user
		#endif

		user.__dict__.update(model_field_dict)
		
		self.update_shib_params(user, kwargs)
		
		user.save()

		return user if self.user_can_authenticate(user) else None

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
