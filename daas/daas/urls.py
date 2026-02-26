"""daas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.urls import include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.staticfiles.urls import staticfiles_urlpatterns as patterns
from django.views.generic.base import RedirectView


def custom_page_not_found(request, exception):
    """Return a plain 404 to avoid DEBUG 404 template crashing on URLResolver.name."""
    return HttpResponse("Not Found", status=404)


handler404 = custom_page_not_found


schema_view = get_schema_view(
   openapi.Info(
      title="DaaS API",
      default_version='v1',
      description="DaaS API Documentation.",
      contact=openapi.Contact(email="lucesposito@deloitte.com"),
      license=openapi.License(name="GNU GPL v3"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'^favicon\.ico$', favicon_view),
    path('', include('daas_app.urls')),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
urlpatterns += patterns()
