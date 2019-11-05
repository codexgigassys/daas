from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


from ..models import Task



@login_required
@permission_required('cancel_job_permission')
def cancel_job_view(request, redis_job_pk):
    Task.objects.get(pk=redis_job_pk).cancel()
    return HttpResponseRedirect(reverse_lazy('index'))
