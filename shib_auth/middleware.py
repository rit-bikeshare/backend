from django.contrib.auth.middleware import RemoteUserMiddleware
from django.core.exceptions import PermissionDenied

from .app_settings import SHIB_FORCE_REAUTH_SESSION_KEY
from .core import ShibAuthCore

class ShibbolethRemoteUserMiddleware(ShibAuthCore, RemoteUserMiddleware):
    """
    Authentication Middleware for use with Shibboleth. Will attempt to authenticate the user on EVERY request
    """
    def process_request(self, request):
		# To support logout. If this variable is True, do not
        # authenticate user and return now.
        if request.session.get(SHIB_FORCE_REAUTH_SESSION_KEY): return
        else:
            # Delete the shib reauth session key if present.
            request.session.pop(SHIB_FORCE_REAUTH_SESSION_KEY, None)

        try: self.login(request)
		except PermissionDenied: pass