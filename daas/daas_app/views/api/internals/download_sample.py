import logging

from ....config import ALLOW_SAMPLE_DOWNLOAD
from ....models import Sample
from ....view_utils import download


def download_sample_view(request, sample_id):
    logging.info('downloading sample: id=%s' % sample_id)
    sample = Sample.objects.get(id=sample_id)
    # With the following 'if' nobody will be allowed to download samples if the config say so,
    # even if they manually craft a download request.
    file_content = sample.data if ALLOW_SAMPLE_DOWNLOAD else b''
    return download(file_content, sample.file_name, "application/octet-stream")
