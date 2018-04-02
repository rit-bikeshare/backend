from django.contrib import admin

class BikeshareAdminSite(admin.AdminSite):
	index_title = site_header = 'Bikeshare administration'
	site_title = 'Bikeshare admin'
	site_url = None

	login_form = logout_template = logout_template = password_change_template = password_change_done_template = None