from django.urls import re_path

from ...views import api

public_api_urlpatterns = [
    re_path(r'^api/get_sample_from_hash/(?P<hash>[a-zA-Z0-9]+)?/?$',
            api.GetSampleFromHashAPIView.as_view(),
            name='api_get_sample_from_hash'),
    re_path(r'^api/upload/?$',
            api.UploadAPIView.as_view(),
            name='api_upload'),
    re_path(r'^api/reprocess/?$',
            api.ReprocessAPIView.as_view(),
            name='api_reprocess'),
    re_path(r'^api/get_token/?$',
            api.get_token_view,
            name='api_get_token'),
    re_path(r'^api/download_source_code/(?P<hash>[a-zA-Z0-9]+)/?$',
            api.DownloadSourceCodeAPIView.as_view(),
            name='download_source_code'),
]
