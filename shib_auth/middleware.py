from django.conf import settings
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import Group
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured

from .app_settings import SHIB_FORCE_REAUTH_SESSION_KEY, SHIB_ATTRIBUTE_MAP, SHIB_MOCK, SHIB_MOCK_ATTRIBUTES, SHIB_USERNAME_ATTRIB_NAME


class ShibbolethRemoteUserMiddleware(RemoteUserMiddleware):
    """
    Authentication Middleware for use with Shibboleth.  Uses the recommended pattern
    for remote authentication from: http://code.djangoproject.com/svn/django/tags/releases/1.3/django/contrib/auth/middleware.py
    """
    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")

        # To support logout.  If this variable is True, do not
        # authenticate user and return now.
        if request.session.get(SHIB_FORCE_REAUTH_SESSION_KEY):
            return
        else:
            # Delete the shib reauth session key if present.
            request.session.pop(SHIB_FORCE_REAUTH_SESSION_KEY, None)

        if settings.DEBUG and SHIB_MOCK:
            request.META.update(SHIB_MOCK_ATTRIBUTES)

        username = request.META.get(SHIB_USERNAME_ATTRIB_NAME, None)
        # If we got None or an empty value, this is still an anonymous user.
        if not username:
            return

        # Make sure we have all required Shiboleth elements before proceeding.
        shib_meta, error = self.parse_attributes(request)
        # Add parsed attributes to the session.
        request.session['shib'] = shib_meta
        if error:
            raise ShibbolethValidationError("All required Shibboleth elements not found.  %s" % shib_meta)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(remote_user=username, shib_meta=shib_meta)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)

    @staticmethod
    def parse_attributes(request):
        """
        Parse the incoming Shibboleth attributes and convert them to the internal data structure.
        From: https://github.com/russell/django-shibboleth/blob/master/django_shibboleth/utils.py
        Pull the mapped attributes from the apache headers.
        """
        shib_attrs = {}
        error = False
        meta = request.META
        for header, attr in list(SHIB_ATTRIBUTE_MAP.items()):
            required, name = attr
            value = meta.get(header, None)
            shib_attrs[name] = value
            if not value or value == '':
                if required:
                    error = True
        return shib_attrs, error


class ShibbolethValidationError(Exception):
    pass
