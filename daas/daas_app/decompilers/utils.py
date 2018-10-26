import time
import os
import shutil
from rq import Queue
from redis import Redis
import subprocess
from .decompiler_config import configs
# Needed for 'eval':
from .filters import *


class Relation:
    def __init__(self, filter, queue, worker):
        """
        :param filter: [function(): str -> bool]
        :param queue: redis queue name [str]
        """
        self.filter = filter
        self.queue = queue
        self.worker = 'decompilers.workers.' + worker
        self.job_id = None

    def send_to_queue_if_necessary(self, sample):
        """ Sends the sample to the queue if it fulfills the condition """
        if self.filter(sample):
            self.send_to_queue(sample)

    def send_to_queue(self, sample):
        queue = Queue(self.queue, connection=Redis(host='daas_redis_1'))
        job = queue.enqueue(self.worker,
                            args=({'sample': sample},))
        self.job_id = job.id

    def has_a_job(self):
        return self.job_id is not None


class Broker:
    def __init__(self):
        self.relations = [Relation(eval(config['filter']),
                                   config['identifier'] + '_queue',
                                   config['identifier'] + '_worker') for config in configs]

    def submit_sample(self, sample):
        for relation in self.relations:
            relation.send_to_queue_if_necessary(sample)

    def get_job_id(self):
        if any(relation.has_a_job() for relation in self.relations):
            return [relation.job_id for relation in self.relations if relation.has_a_job()][0]
        else:
            return None


def remove_directory(path):
    remove(path, remove_function=shutil.rmtree)


def remove_file(path):
    remove(path, remove_function=os.remove)


def remove(path, remove_function):
    for i in range(4):
        try:
            remove_function(path)
        except OSError:
            # Sometimes a file descriptor remains open, so we wait and try again
            time.sleep(int(i) + 1)


def has_a_non_empty_file(base_path):
    for path, subdirs, files in os.walk(base_path):
        for name in files:
            file_path = os.path.join(path, name)
            if file_is_not_empty(file_path):
                return True
    return False


def file_is_not_empty(file_path):
    return subprocess.check_output(['du', '-sh', file_path]).split()[0] != '0'
