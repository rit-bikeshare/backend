"""
Django settings for bikeshare project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = None

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

APPEND_SLASH = False

CSRF_COOKIE_AGE = None


# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.gis',

	'constance', # DB-backed settings
	'constance.backends.database',

	'admin_reorder',
	
	'rest_framework',
	
	'shib_auth',

	'app',
	
	'bikeshare'
]

MIDDLEWARE = [
	'admin_reorder.middleware.ModelAdminReorder',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'shib_auth.middleware.ShibbolethRemoteUserMiddleware',
	'bikeshare.middleware.MaintenanceInterceptorMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'wsgi.application'

ADMIN_REORDER = (
	'bikeshare',
	'constance',
	# Cross-linked models
	{'app': 'auth', 'models': ('auth.Group', 'app.BikeshareUser')},
)

# Setting editable through admin interface
from collections import OrderedDict
CONSTANCE_CONFIG = OrderedDict([
	('ENABLE_DROP_ANYWHERE', (False, 'Turn on or off backend support for drop anywhere')),

	('ALLOW_CHECKOUT', (True, 'Should the app allow users to check out a bike')),
	('CHECKOUT_DISALLOWED_MESSAGE', ('Bikeshare checkout has been closed until Spring. Check back later!',
		'Message to display when checkout is disabled and user attempts checkout'
	)),
	('MAINTENANCE_MODE', (False, 'Set to True to disable system')),
	('MAINTENANCE_MESSAGE', ('Bikeshare is currently unavailable. Please try again later.',
		'Message to display when a user accesses the app in mainenance mode'
	)),

	('ADMIN_DEFAULT_LAT', (43.08397722062759, 'Default lat of map in admin interface')),
	('ADMIN_DEFAULT_LON', (-77.67605446140749, 'Default lon of map in admin interface')),
	('ADMIN_DEFAULT_ZOOM', (15, 'Default zoom of map in admin interface')),
])
CONSTANCE_CONFIG_FIELDSETS = {
	'Features': ('ENABLE_DROP_ANYWHERE',),
	'Maintenance Settings': ('ALLOW_CHECKOUT', 'CHECKOUT_DISALLOWED_MESSAGE', 'MAINTENANCE_MODE', 'MAINTENANCE_MESSAGE'),
	'Map Settings': ('ADMIN_DEFAULT_LAT', 'ADMIN_DEFAULT_LON', 'ADMIN_DEFAULT_ZOOM')
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

DATABASES = {}

# Try to use database from ENV
if 'DATABASE_URL' in os.environ:
	try:
		import dj_database_url
		DATABASES['default'] = dj_database_url.config(conn_max_age=600)
	except ImportError:
		from django.core.exceptions import ImproperlyConfigured
		raise ImproperlyConfigured("Found DATABASE_URL variable but couldn't "
		"import dj-database-url package. Did you remember to install it?")

REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': ('app.rest_auth.NoCsrfSessionAuthentication',),

	'DEFAULT_RENDERER_CLASSES': [
		'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
	],

	'DEFAULT_PARSER_CLASSES': [
		'djangorestframework_camel_case.parser.CamelCaseJSONParser',
	],
}

AUTHENTICATION_BACKENDS = (
	'app.backends.BikeshareRemoteUserBackend',
)

SHIB_USERNAME_ATTRIB_NAME = 'uid'
SHIB_ATTRIBUTE_MAP = {
	"uid": (True, "username"),
	"sn": (False, "last_name"),
	"givenName": (False, "first_name")
}

SHIB_MOCK = False
SHIB_MOCK_ATTRIBUTES = {
	'uid': 'test',
	'sn' : 'McTestface',
	'givenName': 'Testy'
}

AUTH_USER_MODEL = 'app.BikeshareUser'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'