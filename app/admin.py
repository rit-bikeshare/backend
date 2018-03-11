from django.contrib.auth.admin import UserAdmin
from django.contrib.gis import admin
from django.utils.translation import gettext, gettext_lazy as _

from . import models, forms

from extended_permissions.admin import ExtendedUserAdminMixin
from django_shib_auth.admin import ShibIgnoredGroupsAdminMixin

 
@admin.register(models.BikeshareUser)
class BikeshareUserAdmin(ExtendedUserAdminMixin, ShibIgnoredGroupsAdminMixin, UserAdmin):
	form = forms.UserChangeForm
	add_form = forms.UserCreationForm

	add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',),
        }),
    )

	def get_urls(self):
		return super().get_urls()[1:] # cut off the change password view
