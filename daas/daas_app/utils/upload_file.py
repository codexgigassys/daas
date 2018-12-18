from django.db import transaction
import hashlib

from ..models import Sample, RedisJob
from . import classifier
from .redis_manager import RedisManager


def upload_file(name, content, force_reprocess=False):
    """
    :param name: <string> File name for the uploaded sample.
    :param content: <bytes> Sample content (file.read() output for instance)
    :param force_reprocess: <bool> If true, the sample will be reprocessed even if it's already processed with the
                            latest version of the decompiler.
    :return: <bool, bool> returns two booleans:
                            1. Whether or not the uploaded file already exists.
                            2. Whether or not we should process the file.
    """
    # send file to the classifier
    identifier = classifier.classify(content)
    job_id = None
    # if it's a sample, save it
    if identifier is not 'zip':
        sha1 = hashlib.sha1(content).hexdigest()
        try:
            with transaction.atomic():
                already_exists = Sample.objects.filter(sha1=sha1).exists()
                if already_exists:
                    sample = Sample.objects.get(sha1=sha1)
                else:
                    sample = Sample.objects.custom_create(name, content, identifier)
                should_process = force_reprocess or (not already_exists) or sample.should_reprocess
                if should_process:
                    _, job_id = RedisManager().submit_sample(content)
                    RedisJob.objects.create(job_id=job_id, sample=sample)
        except Exception as e:
            # Cancel the task in time to avoid unnecessary processing.
            RedisManager().cancel_job(identifier, job_id)
            raise e
    return (already_exists, should_process) if identifier is not 'zip' else (False, False)
