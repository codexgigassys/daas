import datetime
import string
import random
from typing import Dict, List

from .generic import APITestCase
from ....models import RedisJob, Sample, Result
from ....utils.redis_manager import RedisManager
from ....utils.charts.statistics_manager import StatisticsManager
from ...mocks.statistics_redis import StatisticsRedisMock


class AbstractStatisticsTestCase(APITestCase):
    def setUp(self) -> None:
        RedisManager().__mock__()
        self.statistics_manager = StatisticsManager()
        self.statistics_manager._redis = StatisticsRedisMock()
        self.today = datetime.datetime.now().date().isoformat().encode('utf-8')
        self.random_strings = set()
        # Also flush keys here in case there are keys in the db due to unexpected reasons
        # (test aborted before teardown, for instance)
        self.statistics_manager._redis.flush_test_keys()

    def tearDown(self) -> None:
        self.statistics_manager._redis.flush_test_keys()

    def _get_random_with_length(self, length):
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        while random_string in self.random_strings:
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        return bytes(random_string.encode('utf-8'))

    def _create_sample(self, file_type: str, size: int):
        return Sample.objects.create(name='', content=self._get_random_with_length(size) * 1024, file_type=file_type)

    def _create_samples_with_result(self, file_type: str, size: int, amount: int, redis_job_status: int, result_status: int, elapsed_time: int):
        for i in range(amount):
            sample = self._create_sample(file_type=file_type, size=size)
            RedisJob.objects.create(sample=sample, job_id=str(i), status=redis_job_status)
            Result.objects.create(elapsed_time=elapsed_time, status=result_status, decompiler='', sample=sample, output='')

    def _get_statistics_from_redis(self, file_type: str, field: str) -> Dict[bytes, bytes]:
        return self.statistics_manager._redis.get_statistics_for(file_type, field)

    def _get_value_from_redis(self, file_type: str) -> str:
        return self.statistics_manager._redis.get_count_for_file_type(file_type)

    def _write_values_to_redis(self, file_type: str, field: str, value: str, increase=True, times=1) -> None:
        for _ in range(times):
            self.statistics_manager._redis.register_field_and_value(file_type, field, value, increase=increase)

    def _increase_count_for_file_type(self, file_type: str, times: int = 1):
        for _ in range(times):
            self.statistics_manager._redis.register_new_sample_for_type(file_type)

    def _get_iso_formatted_days_before(self, days: int) -> str:
        return (datetime.date.today() - datetime.timedelta(days=days)).isoformat()

    def _captions_to_bytes(self, captions: List[str]) -> List[bytes]:
        return [bytes(caption.encode('utf-8')) for caption in captions]
