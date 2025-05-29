import pickle
pickle.HIGHEST_PROTOCOL = 4
import os
from rq import Queue
from redis import Redis
import logging


class TaskRequeuer:
    def __init__(self):
        # self.connection = Redis(host='redis', ssl=True, ssl_cert_reqs="none", password=os.environ.get('REDIS_PASSWORD'))
        self.connection = Redis(host='redis')
        
        # Where to look for decompilers' code
        self.worker_path = 'daas.worker.worker'
        # Queue for metadata extractor
        self.queue = Queue('unknown_requeued',
                           connection=self.connection,
                           default_timeout=1200)

    def requeue(self, task_arguments: dict) -> None:
        task = self.queue.enqueue(self.worker_path, args=(task_arguments,))
        logging.info(f'Service is unavailable for the given url. Task requeued. {task_arguments["external_url"]=}, {task.id=}')
