import logging
from django.db import transaction

from ..models import Sample, Task
from .status.sample import SampleStatus
from .task_manager import TaskManager


def _process_sample(sample: Sample) -> str:  # fixme rename this. check for duplicated logic.
    _, task_id = TaskManager().submit_sample(sample)
    sample.wipe()  # for reprocessing or non-finished processing.
    Task.objects.create(task_id=task_id, sample=sample)  # assign the new task to the sample
    return task_id


def upload(sha1, force_process=False) -> None:
    logging.info(f'Processing non-zip {self.identifier} file.')
    with transaction.atomic():
        already_exists, sample = Sample.objects.get_sample_with_hash(sha1)
        will_be_processed = sample.requires_processing or force_process
        if will_be_processed and sample.status not in [SampleStatus.QUEUED, SampleStatus.PROCESSING]:
            task_id = _process_sample(sample)
            logging.info(f'File {sha1=} sent to the queue with {task_id=}')
        else:
            logging.info(
                f'File {sha1=} is not going to be processed again, because it\'s not needed and it\'s not foced.')