from django.urls import re_path
from . import views, api
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    re_path(r'^upload_file/?$', views.upload_file_view, name='upload_file'),

    # Statistics views:
    re_path(r'^statistics/samples_per_size/?$', views.SamplesPerSize.as_view(),
            name='samples_per_size'),
    re_path(r'^statistics/samples_per_size_data/?$', api.internals.SamplesPerSizeData.as_view(),
            name='samples_per_size_data'),

    re_path(r'^statistics/samples_per_elapsed_time/?$', views.SamplesPerElapsedTime.as_view(),
            name='samples_per_elapsed_time'),
    re_path(r'^statistics/samples_per_elapsed_time_data/?$', api.internals.SamplesPerElapsedTimeData.as_view(),
            name='samples_per_elapsed_time_data'),

    re_path(r'^statistics/samples_per_type/?$', views.SamplesPerType.as_view(),
            name='samples_per_type'),
    re_path(r'^statistics/samples_per_type_data/?$', api.internals.SamplesPerTypeData.as_view(),
            name='samples_per_type_data'),

    re_path(r'^statistics/samples_per_upload_date/?$', views.SamplesPerUploadDate.as_view(),
            name='samples_per_upload_date'),
    re_path(r'^statistics/samples_per_upload_date_data/?$', api.internals.SamplesPerUploadDateData.as_view(),
            name='samples_per_upload_date_data'),

    re_path(r'^statistics/samples_per_process_date/?$', views.SamplesPerProcessDate.as_view(),
            name='samples_per_process_date'),
    re_path(r'^statistics/samples_per_process_date_data/?$', api.internals.SamplesPerProcessDateData.as_view(),
            name='samples_per_process_date_data'),

    re_path(r'^statistics/samples_per_status/(?P<file_type>[a-zA-Z0-9]+)/?$', views.SamplesPerStatusForFileType.as_view(),
            name='samples_per_status'),
    re_path(r'^statistics/samples_per_status_data/(?P<file_type>[a-zA-Z0-9]+)/?$', api.internals.SamplesPerStatusForFileTypeData.as_view(),
            name='samples_per_status_data'),

    re_path(r'^download_source_code/(?P<sample_id>[0-9]+)/?$',
            views.download_source_code_view,
            name='download_source_code'),
    re_path(r'^download_sample/(?P<sample_id>[0-9]+)/?$', api.download_sample_view, name='download_sample'),
    re_path(r'^delete_sample/(?P<pk>[0-9]+)/?$', views.SampleDeleteView.as_view(), name='delete_sample'),
    re_path(r'^reprocess/(?P<sample_id>[0-9]+)/?$', views.reprocess_view, name='reprocess'),
    re_path(r'^cancel_job/(?P<redis_job_pk>[0-9]+)/?$',
            views.cancel_job_view,
            name='cancel_job'),
    re_path(r'^$', views.IndexRedirectView.as_view(), name='index_redirect'),
    re_path(r'^index/?$', views.IndexView.as_view(), name='index'),
    re_path(r'^file_already_uploaded/?$', views.file_already_uploaded_view, name='file_already_uploaded'),
    re_path(r'^no_filter_found/?$', views.no_filter_found_view, name='no_filter_found'),

    re_path(r'^api/get_sample_from_hash/(?P<hash>[a-zA-Z0-9]+)?$', api.GetSampleFromHashAPIView.as_view(), name='api_get_sample_from_hash'),
    re_path(r'^api/upload/?$', api.UploadAPIView.as_view(), name='api_upload'),
    re_path(r'^api/reprocess/?$', api.ReprocessAPIView.as_view(), name='api_reprocess'),
    re_path(r'^api/get_token/?$', api.get_token_view, name='api_get_token'),

    # Private API (only reachable within the docker network)
    re_path(r'^internal/api/set_result/?$',
            api.internals.SetResultApiView.as_view(),
            name='set_result_internal'),
    re_path(r'^internal/api/download_sample/(?P<sample_id>[0-9]+)/?$',
            api.internals.download_sample_view,
            name='download_sample_internal'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
