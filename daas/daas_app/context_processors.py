from .models import Sample
from .utils.charts.chart_cache import ChartCache


# Increase this number after every release to force browsers to download the latest static files
RELEASE_NUMBER = 10


def release_number(request):
    return {'release_number': "?v=%s" % RELEASE_NUMBER}


def sample_count_context(request):
    context_data = dict()
    context_data['samples_count'] = Sample.objects.finished().count()
    return context_data


def time_since_last_chart_update_context(request):
    context_data = dict()
    context_data['time_since_last_chart_update'] = ChartCache().time_since_last_update_as_string
    return context_data
