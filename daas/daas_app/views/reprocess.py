from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
import logging

from ..models import Sample
from ..utils.reprocess import reprocess


@login_required
@permission_required('upload_sample_permission')
def reprocess_view(request, sample_id):
    logging.info('Reprocessing sample: %s' % sample_id)
    reprocess(Sample.objects.get(id=sample_id), force_reprocess=True)
    return HttpResponseRedirect(reverse('index'))
