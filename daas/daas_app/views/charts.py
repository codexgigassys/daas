from django.urls import reverse
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin


class AbstractChartView(LoginRequiredMixin, generic.View):
    template_name = 'daas_app/chart.html'
    data_url_name = None

    def chart_loader(self):
        return {'id': self.data_url_name.replace('_data', ''),
                'url': reverse(self.data_url_name)}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'chart': self.chart_loader()})


class SamplesPerSize(AbstractChartView):
    data_url_name = 'samples_per_size_data'


class SamplesPerElapsedTime(AbstractChartView):
    data_url_name = 'samples_per_elapsed_time_data'


class SamplesPerType(AbstractChartView):
    data_url_name = 'samples_per_type_data'


class SamplesPerUploadDate(AbstractChartView):
    data_url_name = 'samples_per_upload_date_data'


class SamplesPerProcessDate(AbstractChartView):
    data_url_name = 'samples_per_process_date_data'


class SamplesPerStatusForFileType(AbstractChartView):
    def chart_loader(self, file_type: str):
        return {'id': f'samples_per_status_{file_type}',
                'url': reverse('samples_per_status_data', args=[file_type])}

    def get(self, request, file_type: str, *args, **kwargs):
        return render(request, self.template_name, {'chart': self.chart_loader(file_type)})
