from rq import Queue
from redis import Redis
from .connections.django_server import DjangoServerConfiguration

from .singleton import ThreadSafeSingleton
from .configuration_manager import ConfigurationManager
from ..tests.mocks.redis_job import MockJob


class RedisManager(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.connection = Redis(host='daas_redis_task_queue_1')
        # Where to look for decompilers' code
        self.worker_path = 'decompilers.worker.worker'
        self.queues = {}
        for configuration in ConfigurationManager().get_configurations():
            # We need only one Queue per config, so this should be in the init to
            # ensure that no duplicated Queue instances will be created.
            self.queues[configuration.identifier] = Queue(configuration.queue_name,
                                                          connection=self.connection,
                                                          default_timeout=configuration.timeout + 65)

    def get_queue(self, identifier):
        return self.queues[identifier]

    def get_job(self, identifier, job_id):
        return self.get_queue(identifier).fetch_job(job_id)

    def submit_sample(self, sample):
        configuration = ConfigurationManager().get_config_for_sample(sample)
        queue = self.get_queue(configuration.identifier)
        job = queue.enqueue(self.worker_path,
                            args=({'sample_id': sample.id,
                                   'config': configuration.as_dictionary(),
                                   'api_base_url': DjangoServerConfiguration().base_url},))
        return configuration.identifier, job.id

    def cancel_job(self, identifier, job_id):
        if job_id is not None:
            job = self.get_job(identifier, job_id)
            if job is not None:
                job.cancel()

    """ Test methods: """
    def __mock__(self, identifier='pe', job_id='i-am-a-job'):
        self.__mock_calls_submit_sample = 0
        self.__mock_job = MockJob()
        self.__mock_identifier = identifier
        self.__mock_job_id = job_id
        self.get_job = lambda x=None, y=None: self.__mock_job
        self.submit_sample = self.__submit_sample_mock__
        self.cancel_job = lambda x=None, y=None: None

    def __mock_calls_submit_sample__(self):
        return self.__mock_calls_submit_sample

    def __submit_sample_mock__(self, sample):
        self.__mock_calls_submit_sample += 1
        return ConfigurationManager().get_config_for_sample(sample).identifier, self.__mock_job
