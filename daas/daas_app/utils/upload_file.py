from django.db import transaction
import hashlib
import logging

from ..models import Sample, RedisJob
from . import classifier, zip_distributor
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
    identifier = classifier.get_identifier_of_file(content)
    job_id = None
    if identifier is not 'zip':
        logging.info('upload_file: Processing non-zip %s file.' % identifier)
        sha1 = hashlib.sha1(content).hexdigest()
        with transaction.atomic():
            already_exists, sample = Sample.objects.get_or_create(sha1, name, content, identifier)
            logging.debug('Sample: %s' % sample)
            should_process = force_reprocess or sample.requires_processing
            logging.debug('force_process=%s. requires_processing=%s. Result: should_process=%s' % (force_reprocess, sample.requires_processing, should_process))
            if should_process:
                _, job_id = RedisManager().submit_sample(sample)
                sample.wipe()
                RedisJob.objects.create(job_id=job_id, sample=sample)  # assign the new job to the sample
                logging.info('File %s (sha1) sent to the queue. job_id = %s' % (sha1, job_id))
            else:
                logging.info('This sample (%s) is not going to be processed again, because it\'s not needed and it\'s not foced.' % sha1)
        return already_exists, should_process
    else:
        logging.info('upload_file: Processing zip file. (identifier=%s)' % identifier)
        return zip_distributor.upload_files_of(content)
