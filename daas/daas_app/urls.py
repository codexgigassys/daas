from django.urls import re_path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    re_path(r'^upload_file/?$', views.upload_file, name='upload_file'),
    re_path(r'^$', views.IndexView.as_view(), name='index')
]

#urlpatterns = format_suffix_patterns(urlpatterns)
