import requests
import threading
from typing import Optional, SupportsBytes

from .redis_callbacks import CallbacksRedis
from ..singleton import ThreadSafeSingleton, synchronized
from ...models import Sample
from ...serializers import SampleSerializer


lock = threading.Lock()


class CallbackManager(metaclass=ThreadSafeSingleton):
    def __init__(self) -> None:
        self._redis = CallbacksRedis()

    @synchronized(lock)
    def add_url(self, sample_sha1: str, callback_url: SupportsBytes) -> None:
        self._redis.add_callback(sample_sha1, callback_url)

    @synchronized(lock)
    def send_callbacks(self, sample_sha1: str) -> None:
        for callback_url in self._redis.get_callbacks(sample_sha1):
            self._call(sample_sha1, callback_url)

    def _call(self, sample_sha1: str, callback_url: Optional[SupportsBytes]) -> None:
        if callback_url:
            requests.post(callback_url, SampleSerializer(Sample.objects.get(sha1=sample_sha1)).data)

    """ test methods: """
    def __mock__(self) -> None:
        self.call = lambda sample_sha1, callback_url: None
