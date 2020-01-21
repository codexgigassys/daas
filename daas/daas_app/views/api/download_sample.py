""" Decorated version of 'download_sample' that requires login.
    Use this version for the front end and the public API.
    The internal version is only for workers. """
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from .internals import download_sample_view as internal_download_sample_view


@login_required
@permission_required('download_sample_permission')
def download_sample_view(request, sample_id):
    return internal_download_sample_view(request, sample_id)
