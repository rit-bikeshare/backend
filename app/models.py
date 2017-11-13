from shib_auth.models import AbstractShibUser, ShibUserManager
from extended_auth.models import ExtendedPermissionsMixin

class BikeshareUser(ExtendedPermissionsMixin, AbstractShibUser):
	objects = ShibUserManager()

	def get_full_name(self):
		firstName, lastName = getattr(self, 'first_name', None), getattr(self, 'last_name', None)

		if firstName and lastName: return '{} {}'.format(firstName, lastName)
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
