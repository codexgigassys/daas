from .models import Sample

# Increase this number after every release to force browsers to download the latest static files
RELEASE_NUMBER = 10


def release_number(request):
    return {'release_number': "?v=%s" % RELEASE_NUMBER}


def sample_count_context(request):
    context_data = dict()
    context_data['samples_count'] = Sample.objects.finished().count()  # fixme: replace using redis!
    return context_data
