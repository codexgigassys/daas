from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from .decompilers.utils import RelationRepository
from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Sample, Statistics
import ast
import hashlib
from django.urls import reverse_lazy


class IndexView(generic.View):
    template_name = 'daas_app/index.html'

    def get(self, request):
        samples = Sample.objects.all()
        return render(request, 'daas_app/index.html', {'samples': samples})


class StatisticsView(generic.View):
    """ Decompiled samples per size """
    template_name = 'daas_app/statistics.html'

    def get(self, request):
        size_list = [int(sample.size/1024) for sample in Sample.objects.exclude(statistics__isnull=True) if sample.statistics.exit_status == 0]
        ydata = [0, 0, 0, 0]
        for size in size_list:
            position = len(str(size)) - 2
            ydata[position] += 1
        xdata = ["< 100 Kb", "100 Kb - 1 Mb", "1 Mb - 10 Mb", "> 10 Mb"]
        chartdata = {'x': xdata, 'y': ydata}
        chartdata2 = {'x':xdata, 'y': ydata}
        data = {
            'charttype': "discreteBarChart",
            'chartdata': chartdata,
            'chartdata2': chartdata2,
            'chartcontainer': 'piechart_container',
            'chartcontainer2': 'piechart_container2',
            'extra': {
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': False,
            }
        }
        return render(request, 'daas_app/statistics.html', data)


class SamplesPerElapsedTime(generic.View):
    template_name = 'daas_app/statistics.html'

    def get(self, request):
        times = [statistic.elapsed_time for statistic in Statistics.objects.filter(exit_status=0)]
        ydata = [0, 0, 0, 0, 0, 0, 0]
        for time in times:
            position = int(time/10) if time < 60 else 6
            ydata[position] += 1
        xdata = ["<= 9", "10 - 19", "20 - 29", "30 - 39", "40 - 49", "50 - 59", ">= 60"]
        chartdata = {'x': xdata, 'y': ydata}
        data = {
            'charttype': "discreteBarChart",
            'chartdata': chartdata,
            'chartcontainer': 'piechart_container',
            'extra': {
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': False,
            }
        }
        return render(request, 'daas_app/statistics.html', data)


class SampleDeleteView(generic.edit.DeleteView):
    model = Sample
    success_url = reverse_lazy('index')
    template_name = 'daas_app/sample_confirm_delete.html'
# --------------- #
# --- UPLOADS --- #
# --------------- #
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            content = request.FILES['file'].file.read()
            name = request.FILES['file'].name
            md5 = hashlib.md5(content).hexdigest()
            sha1 = hashlib.sha1(content).hexdigest()
            sha2 = hashlib.sha256(content).hexdigest()
            Sample.objects.create(data=content, md5=md5, sha1=sha1, sha2=sha2, size=len(content), name=name)
            RelationRepository().submit_sample(content)
            return HttpResponseRedirect(reverse('index'))
    else:  # GET
        form = UploadFileForm()
        return render(request, 'daas_app/upload.html', {'form': form})


class SetResult(APIView):
    def post(self, request):
        result = ast.literal_eval(request.POST['result'])
        sample = Sample.objects.get(sha1=result['statistics']['sha1'])
        timeout = result['statistics']['timeout']
        elapsed_time = result['statistics']['elapsed_time']
        exit_status = result['statistics']['exit_status']
        timed_out = result['statistics']['timed_out']
        output = result['statistics']['output']
        errors = result['statistics']['errors']
        decompiled = result['statistics']['decompiled']
        zip = result['zip']
        decompiler = result['statistics']['decompiler']
        statistics = Statistics.objects.create(timeout=timeout, elapsed_time=elapsed_time,
                                               exit_status=exit_status, timed_out=timed_out,
                                               output=output, errors=errors, zip_result=zip,
                                               decompiled=decompiled, decompiler=decompiler)
        sample.statistics = statistics
        sample.save()
        return Response({'message': 'ok'})


# Do not use this function as a view. Use it in other views.
def download(file_content, filename, content_type, extension='.daas'):
    filename += extension
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename  # force browser to download file
    response.write(file_content)
    return response


def download_source_code(request, sample_id):
    sample = Sample.objects.get(id=sample_id)
    file_content = sample.statistics.zip_result
    return download(file_content, sample.name, "application/x-zip-compressed", extension='.zip')


def download_sample(request, sample_id):
    sample = Sample.objects.get(id=sample_id)
    file_content = sample.statistics.zip_result
    return download(file_content, sample.name, "application/octet-stream")
