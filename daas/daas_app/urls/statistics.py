from django.urls import re_path

from .. import views, api


statistics_urlpatterns = [
    re_path(r'^statistics/samples_per_size/?$',
            views.SamplesPerSize.as_view(),
            name='samples_per_size'),
    re_path(r'^statistics/samples_per_size_data/?$',
            api.internals.SamplesPerSizeData.as_view(),
            name='samples_per_size_data'),

    re_path(r'^statistics/samples_per_elapsed_time/?$',
            views.SamplesPerElapsedTime.as_view(),
            name='samples_per_elapsed_time'),
    re_path(r'^statistics/samples_per_elapsed_time_data/?$',
            api.internals.SamplesPerElapsedTimeData.as_view(),
            name='samples_per_elapsed_time_data'),

    re_path(r'^statistics/samples_per_type/?$',
            views.SamplesPerType.as_view(),
            name='samples_per_type'),
    re_path(r'^statistics/samples_per_type_data/?$',
            api.internals.SamplesPerTypeData.as_view(),
            name='samples_per_type_data'),

    re_path(r'^statistics/samples_per_upload_date/?$',
            views.SamplesPerUploadDate.as_view(),
            name='samples_per_upload_date'),
    re_path(r'^statistics/samples_per_upload_date_data/?$',
            api.internals.SamplesPerUploadDateData.as_view(),
            name='samples_per_upload_date_data'),

    re_path(r'^statistics/samples_per_process_date/?$',
            views.SamplesPerProcessDate.as_view(),
            name='samples_per_process_date'),
    re_path(r'^statistics/samples_per_process_date_data/?$',
            api.internals.SamplesPerProcessDateData.as_view(),
            name='samples_per_process_date_data'),

    re_path(r'^statistics/samples_per_status/(?P<file_type>[a-zA-Z0-9]+)/?$',
            views.SamplesPerStatusForFileType.as_view(),
            name='samples_per_status'),
    re_path(r'^statistics/samples_per_status_data/(?P<file_type>[a-zA-Z0-9]+)/?$',
            api.internals.SamplesPerStatusForFileTypeData.as_view(),
            name='samples_per_status_data'),
]
