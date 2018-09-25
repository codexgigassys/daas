from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from .decompilers.utils import RelationRepository
from django.views import generic
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Sample, Statistics
import logging
import ast
import hashlib


class IndexView(generic.View):
    template_name = 'daas_app/index.html'

    def get(self, request):
        samples = Sample.objects.all()
        return render(request, 'daas_app/index.html', {'samples': samples})


class StatisticsView(generic.View):
    template_name = 'daas_app/statistics.html'

    def get(self, request):
        xdata = ["Apple", "Apricot", "Avocado", "Banana", "Boysenberries", "Blueberries", "Dates", "Grapefruit", "Kiwi",
                 "Lemon"]
        ydata = [52, 48, 160, 94, 75, 71, 490, 82, 46, 17]
        chartdata = {'x': xdata, 'y': ydata}
        charttype = "pieChart"
        chartcontainer = 'piechart_container'
        data = {
            'charttype': charttype,
            'chartdata': chartdata,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': False,
            }
        }
        return render(request, 'daas_app/statistics.html', data)
# --------------- #
# --- UPLOADS --- #
# --------------- #
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            content = request.FILES['file'].file.read()
            md5 = hashlib.md5(content).hexdigest()
            sha1 = hashlib.sha1(content).hexdigest()
            sha2 = hashlib.sha256(content).hexdigest()
            sample = Sample.objects.create(data=content, md5=md5, sha1=sha1, sha2=sha2, size=len(content))
            RelationRepository().submit_sample(content)
            return HttpResponseRedirect(reverse('index'))
    else:  # GET
        form = UploadFileForm()
        return render(request, 'daas_app/upload.html', {'form': form})


class SetResult(APIView):
    def post(self, request):
        result = ast.literal_eval(request.POST['result'])
        logging.error(result)
        sample = Sample.objects.get(sha1=result['sha1'])
        timeout = result['timeout']
        elapsed_time = result['elapsed_time']
        exit_status = result['exit_status']
        timed_out = result['timed_out']
        output = result['output']
        errors = result['errors']
        statistics = Statistics.objects.create(timeout=timeout, elapsed_time=elapsed_time, exit_status=exit_status,
                                               timed_out=timed_out, output=output, errors=errors)
        sample.statistics = statistics
        sample.save()
        return Response({'message': 'ok'})
