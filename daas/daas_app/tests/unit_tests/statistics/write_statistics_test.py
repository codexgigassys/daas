from ....models import Sample
from ....utils.status import TaskStatus, ResultStatus
from ...test_utils.test_cases.abstract_chart import AbstractStatisticsTestCase


class SameSampleStatisticsReadTest(AbstractStatisticsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._create_samples_with_result(file_type='flash', size=14, amount=7, task_status=TaskStatus.DONE.value,
                                         result_status=ResultStatus.SUCCESS.value, elapsed_time=13)

    def test_file_type_statistics(self):
        self.assertEquals(self._get_value_from_redis('flash'), 7)

    def test_size_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'size'), {b'14': b'7'})

    def test_uploaded_on_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'uploaded_on'), {self.today: b'7'})

    def test_processed_on_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'processed_on'), {self.today: b'7'})

    def test_elapsed_time_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'elapsed_time'), {b'13': b'7'})

    def test_status_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'status'), {b'0': b'7'})


class DifferentSamplesStatisticsReadTest(AbstractStatisticsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._create_samples_with_result(file_type='pe', size=10, amount=5, task_status=TaskStatus.DONE.value,
                                         result_status=ResultStatus.SUCCESS.value, elapsed_time=13)
        self._create_samples_with_result(file_type='pe', size=20, amount=7, task_status=TaskStatus.FAILED.value,
                                         result_status=ResultStatus.FAILED.value, elapsed_time=5)
        self._create_samples_with_result(file_type='pe', size=110, amount=3, task_status=TaskStatus.DONE.value,
                                         result_status=ResultStatus.SUCCESS.value, elapsed_time=5)

    def test_file_type_statistics(self):
        self.assertEquals(self._get_value_from_redis('pe'), 5 + 7 + 3)

    def test_size_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('pe', 'size'),
                             {b'10': b'5', b'20': b'7', b'110': b'3'})

    def test_uploaded_on_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('pe', 'uploaded_on'),
                             {self.today: bytes(str(5 + 7 + 3).encode('utf-8'))})

    def test_processed_on_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('pe', 'processed_on'),
                             {self.today: bytes(str(5 + 7 + 3).encode('utf-8'))})

    def test_elapsed_time_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('pe', 'elapsed_time'),
                             {b'5': bytes(str(7 + 3).encode('utf-8')), b'13': b'5'})

    def test_status_statistics(self):
        self.assertDictEqual(self._get_statistics_from_redis('pe', 'status'),
                             {b'0': bytes(str(5 + 3).encode('utf-8')), b'2': b'7'})


class DeletedResultRevertsSomeStatisticsReadTest(AbstractStatisticsTestCase):
    """ Deletes one sample's result.
        Therefore, only 'status' and 'elapsed_time' should be reduced by one. """
    def setUp(self) -> None:
        super().setUp()
        self._create_samples_with_result(file_type='flash', size=14, amount=7, task_status=TaskStatus.DONE.value,
                                         result_status=ResultStatus.SUCCESS.value, elapsed_time=13)
        Sample.objects.last().delete()

    def test_file_type_statistics_not_affected(self):
        self.assertEquals(self._get_value_from_redis('flash'), 7)

    def test_size_statistics_not_affected(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'size'), {b'14': b'7'})

    def test_uploaded_on_statistics_not_affected(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'uploaded_on'), {self.today: b'7'})

    def test_processed_on_statistics_not_affected(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'processed_on'), {self.today: b'7'})

    def test_elapsed_time_statistics_reduced_by_one(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'elapsed_time'), {b'13': b'6'})

    def test_status_statistics_reduced_by_one(self):
        self.assertDictEqual(self._get_statistics_from_redis('flash', 'status'), {b'0': b'6'})
