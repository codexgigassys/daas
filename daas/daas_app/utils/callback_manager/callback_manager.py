import logging
import requests
from requests.auth import HTTPBasicAuth
import threading
from typing import Optional, SupportsBytes
from django.conf import settings
from .redis_callbacks import CallbacksRedis
from ..singleton import ThreadSafeSingleton, synchronized
from ...models import Sample
from ...serializers import SampleSerializer

# SUCCESSFUL_DECOMPILATION = 0
auth = getattr(settings, 'DAAS_CODEX_AUTH', None)

lock = threading.Lock()


class CallbackManager(metaclass=ThreadSafeSingleton):
    def __init__(self) -> None:
        self._redis = CallbacksRedis()

    @synchronized(lock)
    def add_url(self, sample_sha1: str, callback_url: Optional[SupportsBytes]) -> None:
        if callback_url:
            self._redis.add_callback(sample_sha1, callback_url)

    @synchronized(lock)
    def send_callbacks(self, sample_sha1: str) -> None:
        for callback_url in self._redis.get_callbacks(sample_sha1):
            self._call(sample_sha1, callback_url)

    def _call(self, sample_sha1: str, callback_url: SupportsBytes) -> None:
        # requests.post(callback_url, SampleSerializer(Sample.objects.get(sha1=sample_sha1)).data)
        sample_to_send = SampleSerializer(
            Sample.objects.get(sha1=sample_sha1)).data

        # Find a better way to retrieve decompiled status.
        # status = sample_to_send['result']['status']
        # sample_to_send['decompiled'] = False
        # if status == SUCCESSFUL_DECOMPILATION:
        #     sample_to_send['decompiled'] = True
        try:
            requests.post(callback_url, sample_to_send, auth=HTTPBasicAuth(
                auth['credentials']['username'], auth['credentials']['password']))
        except requests.exceptions.BaseHTTPError as exception:
            logging.error(f'Error calling {callback_url=} for {sample_sha1=}.')
            logging.exception(exception)

    """ test methods: """

    def __mock__(self) -> None:
        self.call = lambda sample_sha1, callback_url: None
