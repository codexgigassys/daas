from django.urls import reverse
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin


class SamplesPerSize(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/chart.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'daas_app/chart.html', {'data_url': reverse('samples_per_size_data')})


class SamplesPerElapsedTime(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/chart.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'daas_app/chart.html', {'data_url': reverse('samples_per_elapsed_time_data')})


class SamplesPerType(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/chart.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'daas_app/chart.html', {'data_url': reverse('samples_per_type_data')})


class SamplesPerUploadDate(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/chart.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'daas_app/chart.html', {'data_url': reverse('samples_per_upload_date_data')})


class SamplesPerProcessDate(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/chart.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'daas_app/chart.html', {'data_url': reverse('samples_per_process_date_data')})
