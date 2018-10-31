from .singleton import ThreadSafeSingleton
from ..decompilers.decompiler_config import configs
from rq import Queue
from redis import Redis
# Needed for 'eval':
from ..decompilers.filters import *


class RedisManager(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.connection = Redis(host='daas_redis_1')
        self.worker_path = 'decompilers.worker.worker'
        self.queues = {}
        self.configs = {}
        for config in configs:
            # We need only one Queue per config, so this should be in the init to
            # ensure that no duplicated Queue instances will be created.
            queue_name = config['identifier'] + '_queue'
            self.queues[config['identifier']] = Queue(queue_name, connection=self.connection)
            self.configs[config['identifier']] = config

    def get_job(self, identifier, job_id):
        return self.queues[identifier].fetch_job(job_id)

    def fullfils_filter_of(self, sample, config):
        return eval(config['identifier'] + '_filter')(sample)

    def submit_sample(self, sample):
        for identifier, config in self.configs.items():
            if self.fullfils_filter_of(sample, config):
                job = self.queues[identifier].enqueue(self.worker_path,
                                                      args=({'sample': sample, 'config': config},))
                return identifier, job.id

    def cancel_job(self, identifier, job_id):
        job = self.get_job(identifier, job_id)
        if job is not None:
            job.cancel()
