from django_redis import get_redis_connection
from typing import SupportsInt, Dict, Optional


class StatisticsRedis:
    def __init__(self) -> None:
        self._redis = get_redis_connection("default")

    def get_count_for_file_type(self, file_type: str) -> int:
        count_at_redis = self._redis.get(self._get_key(file_type))
        return int(count_at_redis) if count_at_redis else 0

    def register_new_sample_for_type(self, file_type: str) -> None:
        self._redis.incrby(self._get_key(file_type), 1)

    def get_statistics_for(self, file_type: str, field: str) -> Dict[bytes, SupportsInt]:
        return self._redis.hgetall(self._get_key(file_type, field))

    def register_field_and_value(self, file_type: str, field: str, value: str, increase=True) -> None:
        """ For instance, register_at_field(file_type="flash", field="seconds", value="12")
            register that a flash sample needed 12 seconds to be decompiled"""
        self._redis.hincrby(self._get_key(file_type, field), value, 1 if increase else -1)

    def _get_key(self, file_type: str, field: Optional[str] = None) -> str:
        """ Having this method here, we can override it on tests to use different key conventions and avoid wiping
            existing data on development environments. """
        return f'{file_type}:{field}' if field else file_type
