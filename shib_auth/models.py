from django.db import models

# Create your models here.
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin, BaseUserManager

class ShibUserManager(BaseUserManager):
	def create_user(self, username, **kwargs):
		return self.create(username=username)
	#enddef

	def create_superuser(self, username, **kwargs):
		return self.create(username=username, is_superuser=True, is_staff=True)
	#enddef

	def get_by_natural_key(self, username):
		return self.get(**{self.model.USERNAME_FIELD: username})
	#enddef
#endclass

class AbstractShibUser(PermissionsMixin):
	# This class holds some extra info information about users so we can use Django's permissions.
	# Since Shib is used as the SSO, there's no password
	# and user creation is handled automatically by the shib backend.
	# Only the fields we need to store are this model, but the backend
	# may set other attributes directly from shib.

	username = models.CharField(_('username'), max_length=15, primary_key=True)
	last_login = models.DateTimeField(_('last login'), blank=True, null=True)
	is_staff = models.BooleanField(
		_('staff status'),
		default=False,
		help_text=_('Designates whether the user can log into this admin site.'),
	)
	is_active = models.BooleanField(
		_('active'),
		default=True,
		help_text=_(
			'Designates whether this user should be treated as active. '
			'Unselect this instead of deleting accounts.'
		),
	)

	objects = ShibUserManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []


	@property
	def is_anonymous(self):
		"""
		Always return False. This is a way of comparing User objects to
		anonymous users.
		"""
		return False

	@property
	def is_authenticated(self):
		"""
		Always return True. This is a way to tell if the user has been
		authenticated in templates.
		"""
		return True

	def get_username(self):
		return self.username
	#enddef

	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')
		abstract = True
#endclass

# class ShibUser(AbstractShibUser):
# 	objects = ShibUserManager()

# 	def get_full_name(self):
# 		return self.username
# 	#enddef

# 	def get_short_name(self):
# 		return self.username
# 	#endif

# 	def __str__(self):
# 		return self.get_full_name()
# 	#enddef
# #enddef
