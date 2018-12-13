from django.db import transaction
import hashlib

from ..models import Sample, RedisJob
from . import classifier
from .redis_manager import RedisManager


def upload_file(name, content):
    # send file to the classifier
    identifier, job_id = classifier.classify(content)
    # if it's a sample, save it
    if identifier is not 'zip':
        sha1 = hashlib.sha1(content).hexdigest()
        try:
            with transaction.atomic():
                if Sample.objects.filter(sha1=sha1).exists():
                    sample = Sample.objects.get(sha1=sha1)
                else:
                    sample = Sample.objects.custom_create(name, content, identifier)
                RedisJob.objects.create(job_id=job_id, sample=sample)
        except Exception as e:
            # If there where at least one task in queue, the following line will cancel the task in time to avoid
            # unnecessary processing.
            RedisManager().cancel_job(identifier, job_id)
            raise e
