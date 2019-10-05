from django.urls import re_path
from . import views, api
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    re_path(r'^upload_file/?$', views.upload_file_view, name='upload_file'),
    re_path(r'^set_result/?$', views.SetResult.as_view(), name='set_result'),

    re_path(r'^statistics/samples_per_size/?$', views.SamplesPerSize.as_view(),
            name='samples_per_size'),
    re_path(r'^statistics/samples_per_size_data/?$', views.SamplesPerSizeData.as_view(),
            name='samples_per_size_data'),

    re_path(r'^statistics/samples_per_elapsed_time/?$', views.SamplesPerElapsedTime.as_view(),
            name='samples_per_elapsed_time'),
    re_path(r'^statistics/samples_per_elapsed_time_data/?$', views.SamplesPerElapsedTimeData.as_view(),
            name='samples_per_elapsed_time_data'),

    re_path(r'^statistics/samples_per_type/?$', views.SamplesPerType.as_view(),
            name='samples_per_type'),
    re_path(r'^statistics/samples_per_type_data/?$', views.SamplesPerTypeData.as_view(),
            name='samples_per_type_data'),

    re_path(r'^statistics/samples_per_upload_date/?$', views.SamplesPerUploadDate.as_view(),
            name='samples_per_upload_date'),
    re_path(r'^statistics/samples_per_upload_date_data/?$', views.SamplesPerUploadDateData.as_view(),
            name='samples_per_upload_date_data'),

    re_path(r'^statistics/samples_per_process_date/?$', views.SamplesPerProcessDate.as_view(),
            name='samples_per_process_date'),
    re_path(r'^statistics/samples_per_process_date_data/?$', views.SamplesPerProcessDateData.as_view(),
            name='samples_per_process_date_data'),

    #re_path(r'^statistics/samples_per_decompilation_status/?$', views.SamplesPerDecompilationStatusView.as_view(),
    #        name='samples_per_decompilation_status'),
    re_path(r'^download_source_code/(?P<sample_id>[0-9]+)/?$',
            views.download_source_code_view,
            name='download_source_code'),
    re_path(r'^download_sample/(?P<sample_id>[0-9]+)/?$', views.download_sample_view, name='download_sample'),
    re_path(r'^delete_sample/(?P<pk>[0-9]+)/?$', views.SampleDeleteView.as_view(), name='delete_sample'),
    re_path(r'^reprocess/(?P<sample_id>[0-9]+)/?$', views.reprocess_view, name='reprocess'),
    re_path(r'^cancel_job/(?P<redis_job_pk>[0-9]+)/?$',
            views.cancel_job_view,
            name='cancel_job'),
    re_path(r'^$', views.IndexRedirectView.as_view(), name='index_redirect'),
    re_path(r'^index/?$', views.IndexView.as_view(), name='index'),
    re_path(r'^file_already_uploaded/?$', views.file_already_uploaded_view, name='file_already_uploaded'),
    re_path(r'^no_filter_found/?$', views.no_filter_found_view, name='no_filter_found'),

    re_path(r'^api/get_samples_from_hashes/?$', api.GetSamplesFromHashAPIView.as_view(), name='api_get_samples_from_hashes'),
    re_path(r'^api/get_samples_from_file_type/?$', api.GetSamplesFromFileTypeAPIView.as_view(), name='api_get_samples_from_file_type'),
    re_path(r'^api/get_samples_with_size_between/?$', api.GetSamplesWithSizeBetweenAPIView.as_view(), name='api_get_samples_with_size_between'),
    re_path(r'^api/upload/?$', api.UploadAPIView.as_view(), name='api_upload'),
    re_path(r'^api/reprocess/?$', api.ReprocessAPIView.as_view(), name='api_reprocess'),
    re_path(r'^api/get_token/?$', api.get_token, name='api_get_token'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
