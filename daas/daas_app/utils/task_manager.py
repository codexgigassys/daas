import pickle
pickle.HIGHEST_PROTOCOL = 4
from rq import Queue
from rq.job import Job
from redis import Redis
from typing import Tuple, Optional, Dict, Any
from datetime import date
import logging
from threading import Lock
from django.db import transaction

from .connections.django_server import DjangoServerConfiguration
from .singleton import ThreadSafeSingleton
from .configuration_manager import ConfigurationManager
from ..models import Sample
from .status.sample import SampleStatus


_task_lock = Lock()


class TaskManager(metaclass=ThreadSafeSingleton):
    def __init__(self) -> None:
        self.metadata_extractor_connected = True
        self.decompilers_connected = True
        self.send_decompilation_tasks_to_test_queue = False
        self.connection = Redis(host='daas_redis_task_queue_1')
        
        # Comment the line above and uncomment the line below to work with k8s cluster
        # self.connection = Redis(host='redis-task-queue')
        
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
        self.queues['unknown'] = Queue('unknown', connection=self.connection, default_timeout=1200)

        # Queue to use only in tests when necessary
        self.queues['test']  = Queue('test', connection=self.connection, default_timeout=120)

    def get_queue(self, identifier: str) -> Queue:
        return self.queues[identifier] if (not self.send_decompilation_tasks_to_test_queue or identifier == 'unknown') else self.queues['test']

    def get_task(self, identifier: str, task_id: int) -> Job:
        return self.get_queue(identifier).fetch_job(task_id)

    def needs_processing(self, sample: Sample, force_process: bool = False) -> bool:
        non_intermediate_status = sample.status not in [SampleStatus.QUEUED, SampleStatus.PROCESSING]
        return (sample.requires_processing or force_process) and non_intermediate_status

    def submit_sample(self, sample: Sample, force_process: bool = False) -> bool:
        # Use locks to not push the same file two times. After the first push, the second one will return
        # self.needs_processing() => False, and the second copy of the file will not be pushed to the queue.
        sample_submitted = False
        _task_lock.acquire()
        if self.needs_processing(sample, force_process) and (configuration := ConfigurationManager().get_config_for_sample(sample)):
            task = self.enqueue_task(self.get_queue(configuration.identifier),
                                     task_arguments=({'seaweedfs_file_id': sample.seaweedfs_file_id,
                                                      'config': configuration.as_dictionary(),
                                                      'api_base_url': DjangoServerConfiguration().base_url},),
                                     should_enqueue_task=self.decompilers_connected)
            task_id = task.id if task else 'testing'
            from ..models import Task  # To avoid circular imports
            with transaction.atomic():
                sample.wipe()  # for reprocessing or non-finished processing.
                Task.objects.create(task_id=task_id, sample=sample)  # assign the new task to the sample
            sample_submitted = True
            logging.info(f'File {sample.sha1=} sent to the queue with {task_id}')
        else:
            logging.info(f'Processing was requested for file {sample.sha1=} but it is unneeded.')
        _task_lock.release()
        return sample_submitted

    def cancel_task(self, identifier: str, task_id: int) -> None:
        if task_id is not None:
            task = self.get_task(identifier, task_id)
            if task is not None:
                task.cancel()

    def submit_url_for_metadata_extractor(self, zip_password: str, force_reprocess: bool, callback: str,
                                          file_name: str, seaweedfs_file_id: Optional[str] = None,
                                          external_url: Optional[str] = None) -> Tuple[str, Optional[str]]:
        task = self.enqueue_task(self.get_queue('unknown'), task_arguments=({'zip_password': zip_password,
                                                                             'force_reprocess': force_reprocess,
                                                                             'callback': callback,
                                                                             'seaweedfs_file_id': seaweedfs_file_id,
                                                                             'file_name': file_name,
                                                                             'external_url': external_url,
                                                                             'uploaded_on': date.today().isoformat(),
                                                                             'api_url': DjangoServerConfiguration().base_url},),
                                 should_enqueue_task=self.metadata_extractor_connected)
        return 'unknown', task.id if task else None

    def enqueue_task(self, queue: Queue, task_arguments: Tuple[Dict[str, Any]],
                     should_enqueue_task: bool = True) -> Optional[Job]:
        """ Sends tasks to queue if the task manager is connected (self.send_tasks == True). """
        return queue.enqueue(self.worker_path, args=task_arguments) if should_enqueue_task else None

    def connect(self) -> None:
        """ Send tasks to the queues. """
        self.metadata_extractor_connected = True
        self.decompilers_connected = True
        self.send_decompilation_tasks_to_test_queue = False

    def disconnect(self, disconnect_metadata_extractor: bool = True, disconnect_decompilers: bool = True) -> None:
        """ Do not send tasks to queues. Useful for testing. """
        self.metadata_extractor_connected = not disconnect_metadata_extractor
        self.decompilers_connected = not disconnect_decompilers

    def redirect_decompilation_to_test_queue(self, send_decompilation_tasks_to_test_queue: bool = False) -> None:
        self.send_decompilation_tasks_to_test_queue = send_decompilation_tasks_to_test_queue

    def reset(self) -> None:
        """ Wipes all queues and reset configuration to default values. """
        self.metadata_extractor_connected = True
        self.decompilers_connected = True
        self.send_decompilation_tasks_to_test_queue = False
        for queue in self.queues.values():
            queue.empty()
