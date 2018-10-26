from .singleton import ThreadSafeSingleton
from ..decompilers.decompiler_config import configs
from rq import Queue
from redis import Redis
# Needed for 'eval':
from ..decompilers.filters import *


class RedisManager(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.connection = Redis(host='daas_redis_1')
        self.worker_path = 'decompilers.workers.'
        self.queues = {}
        self.filters = {}
        for config in configs:
            queue_name = config['identifier'] + '_queue'
            self.queues[config['identifier']] = Queue(queue_name, connection=self.connection)
            self.filters[config['identifier']] = eval(config['filter'])

    def get_job(self, identifier, job_id):
        return self.queues[identifier].fetch_job(job_id)

    def submit_sample(self, sample):
        for identifier, filter in self.filters.items():
            if filter(sample):
                job = self.queues[identifier].enqueue(self.worker_path + identifier + '_worker',
                                                      args=({'sample': sample},))
                return identifier, job.id

    def cancel_job(self, identifier, job_id):
        self.get_job(identifier, job_id).cancel()
