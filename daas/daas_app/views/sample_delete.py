from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from ..models import Sample


class SampleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.DeleteView):
    model = Sample
    success_url = reverse_lazy('index')
    template_name = 'daas_app/sample_confirm_delete.html'
    permission_required = 'daas_app.delete_sample_permission'
