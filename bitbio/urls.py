"""
URL configuration for bitbio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('other_app/', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("", views.account, name="account"),
    path("home/", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("registration/", views.registration, name="registration"),
    path(
        "registration-success/", views.registration_success, name="registration_success"
    ),
    path("users/", include("app_users.urls")),
    path("calculator/", include("calculator.urls")),
    path("health/", views.health_check, name="health_check"),
]

# Serve static files during development
# In production, WhiteNoise middleware handles static files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
