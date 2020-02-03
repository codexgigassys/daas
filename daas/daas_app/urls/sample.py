from django.urls import re_path

from .. import views
from ..views import api


sample_urlpatterns = [
    re_path(r'^upload_file/?$', views.UploadView.as_view(), name='upload_file'),
    re_path(r'^file_already_uploaded/?$', views.file_already_uploaded_view, name='file_already_uploaded'),
    re_path(r'^download_sample/(?P<sample_id>[0-9]+)/?$', api.download_sample_view, name='download_sample'),
    re_path(r'^reprocess/(?P<sample_id>[0-9]+)/?$', views.ReprocessWebView.as_view(), name='reprocess'),
    re_path(r'^delete_sample/(?P<pk>[0-9]+)/?$', views.SampleDeleteView.as_view(), name='delete_sample'),
    re_path(r'^cancel_task/(?P<pk>[0-9]+)/?$', views.cancel_job_view, name='cancel_task')
]
