import pickle
pickle.HIGHEST_PROTOCOL = 4
from rq import Queue
from rq.job import Job
from redis import Redis
from typing import Tuple, Optional
from datetime import date
import logging
from threading import Lock
from django.db import transaction

from .connections.django_server import DjangoServerConfiguration
from .singleton import ThreadSafeSingleton
from .configuration_manager import ConfigurationManager
from ..tests.mocks.task import MockTask
from ..models import Sample
from .status.sample import SampleStatus


_task_lock = Lock()


class TaskManager(metaclass=ThreadSafeSingleton):
    def __init__(self) -> None:
        self.connection = Redis(host='daas_redis_task_queue_1')
        # Where to look for decompilers' code
        self.worker_path = 'daas.worker.worker'
        self.queues = {}
        for configuration in ConfigurationManager().get_configurations():
            # We need only one Queue per config, so this should be in the init to
            # ensure that no duplicated Queue instances will be created.
            self.queues[configuration.identifier] = Queue(configuration.queue_name,
                                                          connection=self.connection,
                                                          default_timeout=configuration.timeout + 65)
        # Queue for metadata extractor
        self.queues['unknown'] = Queue('unknown',
                                       connection=self.connection,
                                       default_timeout=1200)

    def get_queue(self, identifier: str) -> Queue:
        return self.queues[identifier]

    def get_task(self, identifier: str, task_id: int) -> Job:
        return self.get_queue(identifier).fetch_job(task_id)

    def needs_processing(self, sample: Sample, force_process: bool = False) -> bool:
        non_intermediate_status = sample.status not in [SampleStatus.QUEUED, SampleStatus.PROCESSING]
        return (sample.requires_processing or force_process) and non_intermediate_status

    def submit_sample(self, sample: Sample, force_process: bool = False) -> None:
        # Use locks to not push the same file two times. After the first push, the second one will return
        # self.needs_processing() => False, and the second copy of the file will not be pushed to the queue.
        _task_lock.acquire()
        if self.needs_processing(sample, force_process):
            configuration = ConfigurationManager().get_config_for_sample(sample)
            queue = self.get_queue(configuration.identifier)
            task = queue.enqueue(self.worker_path,
                                 args=({'seaweedfs_file_id': sample.seaweedfs_file_id,
                                        'config': configuration.as_dictionary(),
                                        'api_base_url': DjangoServerConfiguration().base_url},))
            with transaction.atomic():
                sample.wipe()  # for reprocessing or non-finished processing.
                from ..models import Task  # To avoid circular imports
                Task.objects.create(task_id=task.id, sample=sample)  # assign the new task to the sample
            logging.info(f'File {sample.sha1=} sent to the queue with {task.id=}')
        else:
            logging.info(f'Processing was requested for file {sample.sha1=} but it is unneeded.')
        _task_lock.release()

    def cancel_task(self, identifier: str, task_id: int) -> None:
        if task_id is not None:
            task = self.get_task(identifier, task_id)
            if task is not None:
                task.cancel()

    def submit_url_for_metadata_extractor(self, zip_password: str, force_reprocess: bool, callback: str,
                                          file_name: str, seaweedfs_file_id: Optional[str] = None,
                                          external_url: Optional[str] = None) -> Tuple[str, int]:
        queue = self.get_queue('unknown')
        task = queue.enqueue(self.worker_path, args=({'zip_password': zip_password,
                                                      'force_reprocess': force_reprocess,
                                                      'callback': callback,
                                                      'seaweedfs_file_id': seaweedfs_file_id,
                                                      'file_name': file_name,
                                                      'external_url': external_url,
                                                      'uploaded_on': date.today().isoformat(),
                                                      'api_url': DjangoServerConfiguration().base_url},))
        return 'unknown', task.id

    """ Test methods: """
    def __mock__(self, identifier='pe', task_id='i-am-a-task') -> None:
        self.__mock_calls_submit_sample = 0
        self.__mock_task = MockTask()
        self.__mock_identifier = identifier
        self.__mock_task_id = task_id
        self.get_task = lambda x=None, y=None: self.__mock_task
        self.submit_sample = self.__submit_sample_mock__
        self.cancel_task = lambda x=None, y=None: None

    def __mock_calls_submit_sample__(self) -> int:
        return self.__mock_calls_submit_sample

    def __submit_sample_mock__(self, sample: Sample, force_reprocess=False):
        self.__mock_calls_submit_sample += 1
        pass
