from django.contrib.auth.admin import UserAdmin
from django.contrib.gis import admin
from django.utils.translation import gettext, gettext_lazy as _

from . import models


@admin.register(models.BikeshareUser)
class BikeshareUserAdmin(UserAdmin):
	fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions', 'user_denied_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
	
	filter_horizontal = ('groups', 'user_permissions', 'user_denied_permissions')
