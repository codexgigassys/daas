from django.urls import re_path, path
from django.views.generic import RedirectView

from .. import views


index_urlpatterns = [
    path('', RedirectView.as_view(url='index', permanent=True), name='index_redirect'),
    re_path(r'^index/?$', views.IndexView.as_view(), name='index'),
]
