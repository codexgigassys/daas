import pickle
pickle.HIGHEST_PROTOCOL = 5
import os
from rq import Queue
from rq.queue import Job
from redis import Redis
import logging
from str_to_bool import str_to_bool


class TaskQueue:
    def __init__(self):
        self.connection = Redis(host=os.environ.get('REDIS_HOST', 'redis'), port=os.environ.get('REDIS_PORT', 6379),
                               ssl=str_to_bool(os.environ.get('REDIS_SSL', 'true')),
                               ssl_cert_reqs="none", password=os.environ.get('REDIS_PASSWORD'))
        # Where to look for decompilers' code
        self.worker_path = 'daas.worker.worker'
        # Queue for metadata extractor
        self.queue = Queue('unknown_requeued',
                           connection=self.connection,
                           default_timeout=1200)

    def _enqueue(self, task_arguments: dict) -> Job:
        return self.queue.enqueue(self.worker_path, args=(task_arguments,))

    def requeue(self, task_arguments: dict) -> None:
        task = self._enqueue(task_arguments)
        logging.info(f'Service is unavailable for the given url. Task requeued. {task_arguments["external_url"]=}, {task.id=}')

    def add_subfile_to_queue(self, old_task_arguments: dict, seaweedfs_file_id: str) -> None:
        new_task_parameters = old_task_arguments.copy()
        new_task_parameters['external_url'] = None
        new_task_parameters['seaweedfs_file_id'] = seaweedfs_file_id
        task = self._enqueue(new_task_parameters)
        logging.info(f'Subfile of a zip file added to queue as new file with {task.id=}')
