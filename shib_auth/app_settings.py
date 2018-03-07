from django.conf import settings

#At a minimum you will need username
default_shib_attributes = {
  "REMOTE_USER": (True, "username"),
} 

SHIB_ATTRIBUTE_MAP = getattr(settings, 'SHIB_ATTRIBUTE_MAP', default_shib_attributes)
SHIB_USERNAME_ATTRIB_NAME = getattr(settings, 'SHIB_USERNAME_ATTRIB_NAME', 'REMOTE_USER')

# Test mode injects the specified shib attributes
# Set to true if you are testing and want to insert sample headers.
SHIB_MOCK = getattr(settings, 'SHIB_MOCK', False)
SHIB_MOCK_ATTRIBUTES = getattr(settings, 'SHIB_MOCK_ATTRIBUTES')
