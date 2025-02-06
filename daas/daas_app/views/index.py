import logging
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse

from ..models import Sample
from ..filters import SampleFilter


class IndexView(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/index.html'
    filterset_class = SampleFilter

    def get(self, request: HttpRequest) -> HttpResponse:
        logging.debug('IndexView.get(). logging test DEBUG')
        logging.info('IndexView.get(). logging test INFO')
        logging.warning('IndexView.get(). logging test WARNING')
        logging.error('IndexView.get(). logging test ERROR')
        sample_filter = SampleFilter(request.GET, queryset=Sample.objects.all())
        return render(request, 'daas_app/index.html', {'sample_filter': sample_filter})
