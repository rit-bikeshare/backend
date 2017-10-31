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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*$#$!#g=14t2hxjgw&itpm*^pqq=j&)u8zrq8cph(ev8v(w9ne'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'constance', # DB-backed settings
    'constance.backends.database',

    'admin_reorder',
    
    'rest_framework',
    
    'shib_auth',
    
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

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'

ADMIN_REORDER = (
    'bikeshare',
    'constance',
    # Cross-linked models
    {'app': 'auth', 'models': ('auth.Group', 'bikeshare.BikeshareUser')},
)

# Setting editable through admin interface
CONSTANCE_CONFIG = {
    'ALLOW_CHECKOUT': (True, 'Should the app allow users to check out a bike'),
    'CHECKOUT_DISALLOWED_MESSAGE': ('Bikeshare checkout has been closed until Spring. Check back later!',
        'Message to display when checkout is disabled and user attempts checkout'
    ),
    'MAINTENANCE_MODE': (False, 'Set to True to disable system'),
    'MAINTENANCE_MESSAGE': ('Bikeshare is currently unavailable. Please try again later.',
        'Message to display when a user accesses the app in mainenance mode'
    )    
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('bikeshare.rest_auth.NoCsrfSessionAuthentication',)
}

AUTHENTICATION_BACKENDS = (
    'bikeshare.backends.BikeshareRemoteUserBackend',
)

SHIB_USERNAME_ATTRIB_NAME = 'uid'
SHIB_ATTRIBUTE_MAP = {
    "uid": (True, "username"),
    "sn": (False, "last_name"),
    "givenName": (False, "first_name")
}

SHIB_MOCK = True
SHIB_MOCK_ATTRIBUTES = {
    'uid': 'test',
    'sn' : 'McTestface',
    'first_name': 'Testy'
}

AUTH_USER_MODEL = 'bikeshare.BikeshareUser'

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
