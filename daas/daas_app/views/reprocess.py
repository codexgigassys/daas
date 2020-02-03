from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views import generic
from django.http import HttpRequest

from .utils.mixins import ReprocessMixin
from ..models import Sample


class ReprocessWebView(ReprocessMixin, generic.View):
    def get(self, request: HttpRequest, sample_id: int) -> HttpResponseRedirect:
        self.reprocess(Sample.objects.filter(id=sample_id))

        return HttpResponseRedirect(reverse('index'))
