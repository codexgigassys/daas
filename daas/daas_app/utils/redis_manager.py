from .singleton import ThreadSafeSingleton
from rq import Queue
from redis import Redis
from .configuration_manager import ConfigurationManager


class RedisManagerException(Exception):
    pass


class RedisManager(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.connection = Redis(host='daas_redis_1')
        self.worker_path = 'decompilers.worker.worker'
        self.queues = {}
        for identifier in ConfigurationManager().get_identifiers():
            # We need only one Queue per config, so this should be in the init to
            # ensure that no duplicated Queue instances will be created.
            queue_name = ConfigurationManager().get_queue_name(identifier)
            self.queues[identifier] = Queue(queue_name, connection=self.connection)

    def get_job(self, identifier, job_id):
        return self.queues[identifier].fetch_job(job_id)

    def submit_sample(self, sample):
        configuration = ConfigurationManager().get_config_for_sample(sample)
        if configuration is not None:
            identifier = configuration['identifier']
            job = self.queues[identifier].enqueue(self.worker_path,
                                                  args=({'sample': sample, 'config': configuration},))
            return identifier, job.id
        else:
            raise RedisManagerException('No filter for the given sample')

    def cancel_job(self, identifier, job_id):
        job = self.get_job(identifier, job_id)
        if job is not None:
            job.cancel()
