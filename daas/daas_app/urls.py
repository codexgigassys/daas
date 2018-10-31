from django.urls import re_path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    re_path(r'^upload_file/?$', views.upload_file, name='upload_file'),
    re_path(r'^set_result/?$', views.SetResult.as_view(), name='set_result'),
    re_path(r'^statistics/?$', views.StatisticsView.as_view(), name='statistics'),
    re_path(r'^download_source_code/(?P<sample_id>[0-9]+)/?$',
            views.download_source_code,
            name='download_source_code'),
    re_path(r'^download_sample/(?P<sample_id>[0-9]+)/?$', views.download_sample, name='download_sample'),
    re_path(r'^delete_sample/(?P<pk>[0-9]+)/?$', views.SampleDeleteView.as_view(), name='delete_sample'),
    re_path(r'^reprocess/(?P<sample_id>[0-9]+)/?$', views.reprocess, name='reprocess'),
    re_path(r'^cancel_job/(?P<redis_job_pk>[0-9]+)/?$',
            views.cancel_job,
            name='cancel_job'),
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^file_already_uploaded/?$', views.file_already_uploaded, name='file_already_uploaded'),
    re_path(r'^no_filter_found/?$', views.no_filter_found, name='no_filter_found')
]

#urlpatterns = format_suffix_patterns(urlpatterns)
