import datetime
from typing import Dict, List
from django.conf import settings

from .generic import APITestCase
from ....models import Task, Sample, Result
from ....utils.task_manager import TaskManager
from ....utils.charts.statistics_manager import StatisticsManager
from ...mocks.statistics_redis import StatisticsRedisMock


class AbstractStatisticsTestCase(APITestCase):
    def setUp(self) -> None:
        TaskManager().disconnect()
        self.statistics_manager = StatisticsManager()
        self.statistics_manager._redis = StatisticsRedisMock()
        self.today = datetime.datetime.now().date().isoformat().encode('utf-8')
        self.random_strings = set()
        # Also flush keys here in case there are keys in the db due to unexpected reasons
        # (tests aborted before teardown, for instance)
        self.statistics_manager._redis.flush_test_keys()

    def tearDown(self) -> None:
        TaskManager().connect()
        self.statistics_manager._redis.flush_test_keys()

    def _create_sample(self, file_type: str, size: int) -> Sample:
        # Use the epoc as a hash, regardless the length of each kind of hash
        hash = str(datetime.datetime.now().timestamp())
        return Sample.objects.create(file_name='', seaweedfs_file_id='1,1111111111', file_type=file_type,
                                     md5=hash, sha1=hash, sha2=hash, size=size * 1024)

    def _create_samples_with_result(self, file_type: str, size: int, amount: int,
                                    task_status: int, result_status: int, elapsed_time: int) -> None:
        for i in range(amount):
            sample = self._create_sample(file_type=file_type, size=size)
            Task.objects.create(sample=sample, task_id=str(i), _status=task_status)
            Result.objects.create(elapsed_time=elapsed_time, status=result_status, decompiler='', sample=sample, output='')

    def _get_statistics_from_redis(self, file_type: str, field: str) -> Dict[bytes, bytes]:
        return self.statistics_manager._redis.get_statistics_for(file_type, field)

    def _get_value_from_redis(self, file_type: str) -> str:
        return self.statistics_manager._redis.get_count_for_file_type(file_type)

    def _write_values_to_redis(self, file_type: str, field: str, value: str, increase: bool = True, times: int = 1) -> None:
        for _ in range(times):
            self.statistics_manager._redis.register_field_and_value(file_type, field, value, increase=increase)

    def _increase_count_for_file_type(self, file_type: str, times: int = 1) -> None:
        for _ in range(times):
            self.statistics_manager._redis.register_new_sample_for_type(file_type)

    def _get_iso_formatted_days_before(self, days: int) -> str:
        return (datetime.date.today() - datetime.timedelta(days=days)).isoformat()

    def _captions_to_bytes(self, captions: List[str]) -> List[bytes]:
        return [bytes(caption.encode('utf-8')) for caption in captions]
