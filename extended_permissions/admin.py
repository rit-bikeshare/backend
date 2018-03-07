import copy
from django.contrib import admin, auth
from django.utils.translation import gettext, gettext_lazy as _

from . import models

class ExtendedUserAdmin(auth.admin.UserAdmin):
	fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions', 'user_denied_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

# admin.site.unregister(auth.models.User)
# admin.site.register(models.ExtendedUser, ExtendedUserAdmin)
