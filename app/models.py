from django.contrib.auth.models import AbstractUser, UserManager
from extended_permissions.models import ExtendedPermissionsMixin

class BikeshareUserManager(UserManager):
	def create_superuser(self, username, email=None, password=None, **extra_fields):
		super().create_superuser(username, email, password, **extra_fields)

class BikeshareUser(ExtendedPermissionsMixin, AbstractUser):
	objects = BikeshareUserManager()
	REQUIRED_FIELDS = []

	def get_full_name(self):
		firstName, lastName = getattr(self, 'first_name', None), getattr(self, 'last_name', None)

		if firstName and lastName: return '{} {}'.format(firstName, lastName).strip()
		if firstName: return firstName
		if lastName: return lastName
		return self.username
	#enddef

	def get_short_name(self):
		if hasattr(self, 'first_name'): return self.first_name
		return self.username
	#endif

	def __str__(self):
		return self.username
	#enddef
