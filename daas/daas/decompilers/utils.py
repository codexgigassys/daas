class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Relation:
    def __init__(self, filter, queue, worker):
        self.filter = filter
        self.queue = queue
        self.worker = worker

    def send_to_queue_if_necessary(self, sample):
        """ Sends the sample to the queue if it fulfills the condition """
        if self.filter(sample):
            self.send_to_queue(sample)

    def send_to_queue(self, sample):
        """ TODO """
        pass


class RelationRepository(Singleton):
    def __init__(self):
        self.relations = []

    def add_relation(self, filter, queue, worker):
        self.relations.append(filter, queue, worker)

    def submit_sample(self, sample):
        for relation in self.relations:
            relation.send_to_queue_if_necessary(sample)
