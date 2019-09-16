from django.db import transaction
import hashlib
import logging

from ..models import Sample, RedisJob
from . import classifier, zip_distributor
from .redis_manager import RedisManager


def upload_file(name: str, content: bytes, force_reprocess: bool = False, zip_password: bytes = None):
    """
    :param name: File name for the uploaded sample.
    :param content: Sample content (file.read() output for instance)
    :param force_reprocess: If true, the sample will be reprocessed even if it's already processed with the
                            latest version of the decompiler.
    :param zip_password: Password for zip files.
    :return: <bool, bool> returns two booleans:
                            1. Whether or not the uploaded file already exists.
                            2. Whether or not we should process the file.
    """
    # send file to the classifier
    identifier = classifier.get_identifier_of_file(content)
    if identifier is not 'zip':
        logging.info(f'upload_file: Processing non-zip {identifier} file.')
        sha1 = hashlib.sha1(content).hexdigest()
        with transaction.atomic():
            already_exists, sample = Sample.objects.get_or_create(sha1, name, content, identifier)
            logging.debug(f'Sample: {sample}')
            should_process = force_reprocess or sample.requires_processing
            logging.debug(f'force_process={force_reprocess}. requires_processing={sample.requires_processing}. Result: should_process={should_process}')
            if should_process:
                _, job_id = RedisManager().submit_sample(sample)
                if sample.has_redis_job:
                    sample.redisjob.delete()  # delete the old redis job
                RedisJob.objects.create(job_id=job_id, sample=sample)  # assign the new job to the sample
                logging.info(f'File %s ({sha1}) sent to the queue. job_id = {job_id}')
            else:
                logging.info(f'This sample ({sha1}) is not going to be processed again, because it\'s not needed and it\'s not foced.')
        return already_exists, should_process
    else:
        logging.info(f'upload_file: Processing zip file with password {zip_password}. (identifier={identifier})')
        return zip_distributor.upload_files_of(content, zip_password)
