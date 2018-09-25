from .models import Sample


def sample_count_context(request):
    context_data = dict()
    context_data['samples_count'] = Sample.objects.exclude(statistics__isnull=True).count()
    return context_data
