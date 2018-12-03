import hashlib

from .redis_manager import RedisManager, RedisManagerException
from ..config import SAVE_SAMPLES
from ..models import Sample, RedisJob


def upload_file(name, content):
    md5 = hashlib.md5(content).hexdigest()
    sha1 = hashlib.sha1(content).hexdigest()
    sha2 = hashlib.sha256(content).hexdigest()
    # We are going to add file_type and redis_job later
    sample = Sample.objects.create(data=(content if SAVE_SAMPLES else None), md5=md5,
                                   sha1=sha1, sha2=sha2, size=len(content), name=name,
                                   file_type=None)
    try:
        process_file(sample, content)
    except RedisManagerException as e:  # fix it!
        sample.delete()
        raise e


def process_file(sample, content):
    file_type, job_id = RedisManager().submit_sample(content)
    RedisJob.objects.create(job_id=job_id, sample=sample)
    sample.file_type = file_type
    sample.save()
