from django.contrib.auth.decorators import user_passes_test, permission_required as __permission_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def login_required(function=None):
    """
    Decorator for views that checks that the user is logged in, raising a 403 otherwise
    """
	def check_auth(user):
		if user.is_authenticated: return True
		raise PermissionDenied()
	
	actual_decorator = user_passes_test(check_auth)
    if function:
        return actual_decorator(function)
    return actual_decorator

def permission_required(perm):
	return __permission_required(perm, raise_exception=True)

@login_required()
@require_POST()
@permission_required('bikeshare.rent_bike')
def checkout(request):
	pass
