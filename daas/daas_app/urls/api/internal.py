from django.urls import re_path

from ... import api

internal_api_urlpatterns = [
    # Private API (only reachable within the docker network)
    re_path(r'^internal/api/set_result/?$',
            api.internals.SetResultApiView.as_view(),
            name='set_result_internal'),
    re_path(r'^internal/api/download_sample/(?P<sample_id>[0-9]+)/?$',
            api.internals.download_sample_view,
            name='download_sample_internal'),
]
