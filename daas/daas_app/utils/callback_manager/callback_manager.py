import requests
import threading

from .redis_callbacks import CallbacksRedis
from ..singleton import ThreadSafeSingleton, synchronized
from ...models import Sample
from ...serializers import SampleSerializer


lock = threading.Lock()


class CallbackManager(metaclass=ThreadSafeSingleton):
    # Todo: Use redis to store callbacks instead of variables on the API container.
    def __init__(self) -> None:
        self._redis = CallbacksRedis()

    @synchronized(lock)
    def add_url(self, sample_id: int, callback_url: str) -> None:
        self._redis.add_callback(sample_id, callback_url)

    @synchronized(lock)
    def send_callbacks(self, sample_id: int) -> None:
        for callback_url in self._redis.get_callbacks():
            self.call(sample_id, callback_url)

    def call(self, sample_id: int, callback_url: str) -> None:
        requests.post(callback_url, SampleSerializer(Sample.objects.get(id=sample_id)).data)

    """ test methods: """
    def __mock__(self) -> None:
        self.call = lambda url, sha1: None
