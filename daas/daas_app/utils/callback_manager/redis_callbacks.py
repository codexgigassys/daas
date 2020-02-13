from django_redis import get_redis_connection
from typing import List


class CallbacksRedis:
    def __init__(self) -> None:
        self._redis = get_redis_connection("default")

    def add_callback(self, sample_id: int, callback_url: str) -> None:
        self._redis.sadd(sample_id, callback_url)

    def get_callbacks(self, sample_id: int) -> List[bytes]:
        return self._redis.spop(sample_id, 999999)
