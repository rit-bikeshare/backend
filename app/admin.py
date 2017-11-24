from django.contrib.auth.admin import UserAdmin
from django.contrib.gis import admin
from django.utils.translation import gettext, gettext_lazy as _

from . import models, forms


@admin.register(models.BikeshareUser)
class BikeshareUserAdmin(UserAdmin):
	form = forms.UserChangeForm
	add_form = forms.UserCreationForm

	add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',),
        }),
    )

	fieldsets = (
		(None, {'fields': ('username',)}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
									   'groups', 'user_permissions', 'user_denied_permissions')}),
		(_('Important dates'), {'fields': ('last_login',)}),
	)
	
	filter_horizontal = ('groups', 'user_permissions', 'user_denied_permissions')

	def get_urls(self):
		return super().get_urls()[1:] # cut off the change password view
