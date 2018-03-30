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
from django.conf.urls import url, include
from django.contrib.gis import admin

# This should be changed if shib is used
USE_SHIB = getattr(settings, 'USE_SHIB', True)
urlpatterns = [
	url(r'^', include('bikeshare.urls')),
]

if USE_SHIB:
	from . import views
	urlpatterns += [
		url(r'^login/', views.JwtLoginView.as_view()),
		url(r'^logout/', views.JwtLogoutView.as_view()),
	]
else:
	from rest_framework_jwt.views import obtain_jwt_token
	from django.http import HttpResponse
	urlpatterns += [
		url(r'^login/', obtain_jwt_token),
        url(r'^logout/', lambda r: HttpResponse("{'success': true}")),
	]
