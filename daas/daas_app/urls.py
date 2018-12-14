from django.urls import re_path
from . import views, api
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    re_path(r'^upload_file/?$', views.upload_file_view, name='upload_file'),
    re_path(r'^set_result/?$', views.SetResult.as_view(), name='set_result'),
    re_path(r'^statistics/?$', views.StatisticsView.as_view(), name='statistics'),
    re_path(r'^update_statistics/?$', views.UpdateStatisticsViews.as_view(), name='update_statistics'),
    re_path(r'^download_source_code/(?P<sample_id>[0-9]+)/?$',
            views.download_source_code,
            name='download_source_code'),
    re_path(r'^download_sample/(?P<sample_id>[0-9]+)/?$', views.download_sample, name='download_sample'),
    re_path(r'^delete_sample/(?P<pk>[0-9]+)/?$', views.SampleDeleteView.as_view(), name='delete_sample'),
    re_path(r'^reprocess_view/(?P<sample_id>[0-9]+)/?$', views.reprocess, name='reprocess'),
    re_path(r'^cancel_job/(?P<redis_job_pk>[0-9]+)/?$',
            views.cancel_job,
            name='cancel_job'),
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^file_already_uploaded/?$', views.file_already_uploaded, name='file_already_uploaded'),
    re_path(r'^no_filter_found/?$', views.no_filter_found, name='no_filter_found'),

    re_path(r'^api/get_samples_from_hashes/?$', api.GetSamplesFromHashAPIView.as_view(), name='api_get_samples_from_hashes'),
    re_path(r'^api/get_samples_from_file_type/?$', api.GetSamplesFromFileTypeAPIView.as_view(), name='api_get_samples_from_file_type'),
    re_path(r'^api/get_samples_with_size_between/?$', api.GetSamplesWithSizeBetweenAPIView.as_view(), name='api_get_samples_with_size_between')
]

urlpatterns = format_suffix_patterns(urlpatterns)
