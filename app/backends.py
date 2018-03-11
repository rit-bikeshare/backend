from extended_permissions.backends import ExtendedModelBackend
from django_shib_auth.backends import ShibbolethBackend

class BikeshareDummyBackend(ExtendedModelBackend): pass
class BikeshareShibBackend(ExtendedModelBackend, ShibbolethBackend): pass