"""bikeshare URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.conf.urls import url, include
	2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path, include

from . import views

# This should be changed if shib is used
USE_SHIB = getattr(settings, 'USE_SHIB', True)
urlpatterns = [
	path('', include('bikeshare.urls')),
]

if USE_SHIB:
	urlpatterns += [
		path('login/', views.JwtLoginView.as_view()),
		path('logout/', views.JwtLogoutView.as_view()),
	]
else:
	from rest_framework_jwt.views import obtain_jwt_token
	from django.http import HttpResponse
	urlpatterns += [
		path('login/', obtain_jwt_token),
		path('logout/', lambda r: HttpResponse("{'success': true}")),
	]

if getattr(settings, 'USE_ADMIN', False):
	# Patch the admin urls and add them
	from django.contrib.gis import admin
	admin_patterns = [
		path('login/', views.AdminLogin.as_view()),
		path('', admin.site.urls)
	]

	urlpatterns += [
		path('db-admin/', include(admin_patterns))
	]
