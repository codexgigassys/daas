import time
import os
import shutil
from rq import Queue
from redis import Redis
from .filters import pe_filter, flash_filter
import subprocess


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Relation:
    def __init__(self, filter, queue, worker):
        """
        :param filter: [function(): str -> bool]
        :param queue: redis queue name [str]
        """
        self.filter = filter
        self.queue = queue
        self.worker = 'decompilers.decompiler.' + worker

    def send_to_queue_if_necessary(self, sample):
        """ Sends the sample to the queue if it fulfills the condition """
        if self.filter(sample):
            self.send_to_queue(sample)

    def send_to_queue(self, sample):
        queue = Queue(self.queue, connection=Redis(host='daas_redis_1'))
        queue.enqueue(self.worker,
                      args=({'sample': sample},),
                      timeout=9999)


class RelationRepository(Singleton):
    def __init__(self):
        self.relations = [Relation(pe_filter, "pe_queue", "pe_redis_worker"),
                          Relation(flash_filter, "flash_queue", "flash_redis_worker")]

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


def has_a_non_empty_file(base_path):
    for path, subdirs, files in os.walk(base_path):
        for name in files:
            file_path = os.path.join(path, name)
            if file_is_not_empty(file_path):
                return True
    return False


def file_is_not_empty(file_path):
    return subprocess.check_output(['du', '-sh', file_path]).split()[0] != '0'
