from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404

from ..models import Task


@login_required
@permission_required('cancel_job_permission')
def cancel_job_view(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    task = get_object_or_404(Task, pk=pk)
    task.cancel()
    return HttpResponseRedirect(reverse_lazy('index'))
