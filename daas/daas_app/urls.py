from django.urls import re_path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    re_path(r'^upload_file/?$', views.upload_file, name='upload_file'),
    re_path(r'^set_result/?$', views.SetResult.as_view(), name='set_result'),
    re_path(r'^statistics/?$', views.StatisticsView.as_view(), name='statistics'),
    re_path(r'^download_source_code/(?P<sample_id>[0-9]+)/?$', views.download_source_code, name='download_source_code'),
    re_path(r'^$', views.IndexView.as_view(), name='index')
]

#urlpatterns = format_suffix_patterns(urlpatterns)
