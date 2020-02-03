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
        sample_filter = SampleFilter(request.GET, queryset=Sample.objects.all())
        return render(request, 'daas_app/index.html', {'sample_filter': sample_filter})
