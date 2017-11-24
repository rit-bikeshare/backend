from shib_auth.backends import ShibbolethRemoteUserBackend
from extended_auth.backends import ExtendedModelBackend

class BikeshareRemoteUserBackend(ShibbolethRemoteUserBackend, ExtendedModelBackend):
	def update_shib_params(self, user, params):
		user.set_unusable_password()
