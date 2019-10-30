from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
import logging

from ..models import Sample
from ..view_utils import download


@login_required
@permission_required('download_source_code_permission')
def download_source_code_view(request, sample_id):
    logging.info(f'Downloading source code: {sample_id=}')
    sample = Sample.objects.get(id=sample_id)
    zipped_source_code = sample.result.compressed_source_code.tobytes()
    return download(zipped_source_code, sample.name, "application/x-zip-compressed", extension=sample.result.extension)
