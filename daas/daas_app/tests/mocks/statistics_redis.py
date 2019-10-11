from ...utils.charts.statistics_redis import StatisticsRedis


class StatisticsRedisMock(StatisticsRedis):
    """ This class behaves in the same way as its parent class, but uses different keys to store the data, to avoid
        mixing the test information with already existing information. """
    def __init__(self):
        super().__init__()
        self.key_test_prefix = 'test_'

    def _get_key(self, file_type: str, field: str = None) -> str:
        return f'{self.key_test_prefix}{super()._get_key(file_type, field)}'

    def flush_test_keys(self):
        for test_key in self._redis.scan_iter(f'{self.key_test_prefix}*'):
            self._redis.delete(test_key)
