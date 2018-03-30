from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*$#$!#g=14t2hxjgw&itpm*^pqq=j&)u8zrq8cph(ev8v(w9ne'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

SHIB_MOCK = True

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append('rest_framework.renderers.BrowsableAPIRenderer')

from datetime import timedelta
JWT_AUTH['JWT_EXPIRATION_DELTA'] = timedelta(days=365)
