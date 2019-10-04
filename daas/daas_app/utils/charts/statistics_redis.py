from django_redis import get_redis_connection
from typing import SupportsInt, Dict


class StatisticsRedis:
    def __init__(self) -> None:
        self._redis = get_redis_connection("default")

    def flush(self) -> None:
        self._redis.flushall()

    def get_count_for_file_type(self, file_type: str) -> int:
        count_at_redis = self._redis.get(file_type)
        return int(count_at_redis) if count_at_redis else 0

    def get_statistics_for(self, file_type: str, field: str) -> Dict[bytes, SupportsInt]:
        return self._redis.hgetall(f'{file_type}:{field}')

    def register_field_and_value(self, file_type: str, field: str, value: str, increase=True) -> None:
        """ For instance, register_at_field(file_type="flash", field="seconds", value="12")
            register that a flash sample needed 12 seconds to be decompiled"""
        self._redis.hincrby(f'{file_type}:{field}', value, 1 if increase else -1)

    def register_new_sample_for_type(self, file_type: str) -> None:
        self._redis.incrby(file_type, 1)
