from django.apps import AppConfig

class DefaultAppConfig(AppConfig):
	name = 'app'

	def ready(self):
		from django.conf import settings

		if not getattr(settings, 'USE_ADMIN', False): return
		# Swap out the default admin site with ours

		from django.contrib import admin
		from django.contrib.admin import sites
		from .admin_site import BikeshareAdminSite

		mysite = BikeshareAdminSite()
		admin.site = mysite
		sites.site = mysite
