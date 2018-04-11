from django.urls import path, include
from rest_framework import routers

from .app_api.urls import urlpatterns as app_urls
from .admin_api.urls import urlpatterns as admin_urls

from.import views

userUrls = [
	path('info/', views.UserInfoView.as_view()),
]

urlpatterns = [
	path('', include(app_urls)),
	path('admin/', include(admin_urls)),
	path('status/', views.StatusView.as_view()),
	path('user/', include(userUrls)),
]
