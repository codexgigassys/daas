import time
import os
import shutil
from rq import Queue
from redis import Redis
from .filters import pe_filter


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Relation:
    def __init__(self, filter, queue):
        """
        :param filter: [function(): str -> bool]
        :param queue: redis queue name [str]
        """
        self.filter = filter
        self.queue = queue

    def send_to_queue_if_necessary(self, sample):
        """ Sends the sample to the queue if it fulfills the condition """
        if self.filter(sample):
            self.send_to_queue(sample)

    def send_to_queue(self, sample):
        queue = Queue("pe_queue", connection=Redis(host='daas_redis_1'))
        queue.enqueue('decompilers.decompiler.pe_worker_for_redis',
                      args=({'sample': sample},),
                      timeout=9999)


class RelationRepository(Singleton):
    def __init__(self):
        self.relations = [Relation(pe_filter, "pe_queue")]

    def add_relation(self, filter, queue, worker):
        self.relations.append(filter, queue, worker)

    def submit_sample(self, sample):
        for relation in self.relations:
            relation.send_to_queue_if_necessary(sample)


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
