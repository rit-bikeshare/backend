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
    url(r'^admin/', admin.site.urls),
]

if USE_SHIB:
    import shib_auth.views as shib_views
    urlpatterns += [
        url(r'^login/', shib_views.LoginView.as_view()),
        url(r'^logout/', shib_views.LogoutView.as_view()),
    ]
else:
    # Not allowing creation or reset in case this somehow goes live
    import django.contrib.auth.views as auth_views
    from django.shortcuts import render
    urlpatterns += [
        url(r'^login/', auth_views.login),
        url(r'^logout/', auth_views.logout),
        url(r'^accounts/profile', lambda r: render(r, 'registration/success.html'))
    ]
