import requests
import threading

from .singleton import ThreadSafeSingleton, synchronized
from ..models import Sample
from ..serializers import ResultSerializer


lock = threading.Lock()


class CallbackManager(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.urls = {}

    @synchronized(lock)
    def add_url(self, url, sha1):
        self.urls[sha1] = [url] if sha1 not in self.urls else list(set(self.urls[sha1] + [url]))

    @synchronized(lock)
    def call_from_sha1(self, sha1):
        urls = self.urls.pop(sha1)
        for url in urls:
            self.call(url, sha1)

    def call(self, url, sha1):
        requests.post(url, ResultSerializer(Sample.objects.get(sha1=sha1).result).data)
