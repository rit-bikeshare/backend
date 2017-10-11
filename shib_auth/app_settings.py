from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

#At a minimum you will need username, 
default_shib_attributes = {
  "REMOTE_USER": (True, "username"),
} 

SHIB_ATTRIBUTE_MAP = getattr(settings, 'SHIBBOLETH_ATTRIBUTE_MAP', default_shib_attributes)
#Set to true if you are testing and want to insert sample headers.
SHIB_MOCK_HEADERS = getattr(settings, 'SHIBBOLETH_MOCK_HEADERS', False)

#Name of key.  Probably no need to change this.  
LOGOUT_SESSION_KEY = getattr(settings, 'SHIBBOLETH_FORCE_REAUTH_SESSION_KEY', 'shib_force_reauth')
