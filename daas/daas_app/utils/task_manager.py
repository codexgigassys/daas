import pickle
pickle.HIGHEST_PROTOCOL = 4
from rq import Queue
from redis import Redis
from .connections.django_server import DjangoServerConfiguration

from .singleton import ThreadSafeSingleton
from .configuration_manager import ConfigurationManager
from ..tests.mocks.task import MockTask


class TaskManager(metaclass=ThreadSafeSingleton):
    def __init__(self):
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

    def get_queue(self, identifier):
        return self.queues[identifier]

    def get_task(self, identifier, task_id):
        return self.get_queue(identifier).fetch_job(task_id)

    def submit_sample(self, sample):
        configuration = ConfigurationManager().get_config_for_sample(sample)
        queue = self.get_queue(configuration.identifier)
        task = queue.enqueue(self.worker_path,
                            args=({'sample_id': sample.id,
                                   'config': configuration.as_dictionary(),
                                   'api_base_url': DjangoServerConfiguration().base_url},))
        return configuration.identifier, task.id

    def cancel_task(self, identifier, task_id):
        if task_id is not None:
            task = self.get_task(identifier, task_id)
            if task is not None:
                task.cancel()

    """ Test methods: """
    def __mock__(self, identifier='pe', task_id='i-am-a-task'):
        self.__mock_calls_submit_sample = 0
        self.__mock_task = MockTask()
        self.__mock_identifier = identifier
        self.__mock_task_id = task_id
        self.get_task = lambda x=None, y=None: self.__mock_task
        self.submit_sample = self.__submit_sample_mock__
        self.cancel_task = lambda x=None, y=None: None

    def __mock_calls_submit_sample__(self):
        return self.__mock_calls_submit_sample

    def __submit_sample_mock__(self, sample):
        self.__mock_calls_submit_sample += 1
        return ConfigurationManager().get_config_for_sample(sample).identifier, self.__mock_task
