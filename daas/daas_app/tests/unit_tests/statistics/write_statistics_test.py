from ....utils.charts.statistics_manager import StatisticsManager
from ...test_utils.test_cases.abstract_chart import AbstractStatisticsTestCase
from ....utils.status import ResultStatus


class SizeStatisticsWriteTest(AbstractStatisticsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._write_values_to_redis('flash', 'size', '10', times=5)
        self._write_values_to_redis('flash', 'size', '12', times=2)
        self._write_values_to_redis('flash', 'size', '6', times=1)

    def test_size_for_file_type_captions(self):
        self.assertEquals(StatisticsManager().get_size_statistics_for_file_type('flash').captions,
                          ['0 - 1', '2 - 3', '4 - 7', '8 - 15'])

    def test_size_for_file_type_counts(self):
        self.assertEquals(StatisticsManager().get_size_statistics_for_file_type('flash').counts,
                          [0, 0, 1, 7])

    def test_size_for_file_type_captions_affected_by_other_file_types(self):
        self._write_values_to_redis('pe', 'size', '30', times=1)
        self.assertEquals(StatisticsManager().get_size_statistics_for_file_type('flash').captions,
                          ['0 - 1', '2 - 3', '4 - 7', '8 - 15', '16 - 31'])

    def test_size_for_file_type_counts_affected_by_other_file_types(self):
        """ The count list should be longer, but the number of samples for each bar of the
            chart should remain the same. """
        self._write_values_to_redis('pe', 'size', '30', times=1)
        self.assertEquals(StatisticsManager().get_size_statistics_for_file_type('flash').counts,
                          [0, 0, 1, 7, 0])


class ElapsedTimeStatisticsWriteTest(AbstractStatisticsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._write_values_to_redis('java', 'elapsed_time', '6', times=5)
        self._write_values_to_redis('java', 'elapsed_time', '6', times=1)
        self._write_values_to_redis('java', 'elapsed_time', '2', times=2)

    def test_elapsed_time_for_file_type_captions(self):
        self.assertEquals(StatisticsManager().get_elapsed_time_statistics_for_file_type('java').captions,
                          ['0 - 1', '2 - 3', '4 - 7'])

    def test_elapsed_time_for_file_type_counts(self):
        self.assertEquals(StatisticsManager().get_elapsed_time_statistics_for_file_type('java').counts,
                          [0, 2, 6])

    def test_elapsed_time_for_file_type_captions_affected_by_other_file_types(self):
        self._write_values_to_redis('pe', 'size', '30', times=1)
        self.assertEquals(StatisticsManager().get_elapsed_time_statistics_for_file_type('java').captions,
                          ['0 - 1', '2 - 3', '4 - 7'])

    def test_elapsed_time_for_file_type_counts_affected_by_other_file_types(self):
        """ The count list should be longer, but the number of samples for each bar of the
            chart should remain the same. """
        self._write_values_to_redis('pe', 'elapsed_time', '30', times=1)
        self._write_values_to_redis('flash', 'elapsed_time', '7', times=4)
        self.assertEquals(StatisticsManager().get_elapsed_time_statistics_for_file_type('java').counts,
                          [0, 2, 6, 0, 0])


class FileTypeStatisticsWriteTest(AbstractStatisticsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._increase_count_for_file_type('flash', times=5)
        self._increase_count_for_file_type('java', times=3)
        self._increase_count_for_file_type('pe', times=2)

    def test_file_type_captions_and_counts(self):
        self.assertEquals(StatisticsManager().get_sample_count_per_file_type(),
                          [('pe', 2), ('flash', 5), ('java', 3)])


class StatusStatisticsWriteTest(AbstractStatisticsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._write_values_to_redis('pe', 'status', ResultStatus.TIMED_OUT.value, times=1)
        self._write_values_to_redis('pe', 'status', ResultStatus.SUCCESS.value, times=44)
        self._write_values_to_redis('pe', 'status', ResultStatus.FAILED.value, times=6)

    def test_file_type_captions_and_counts(self):
        self.assertEquals(StatisticsManager().get_sample_count_per_status_for_type('pe'),
                          [('Timed_out', 1), ('Success', 44), ('Failed', 6)])


class ProcessDateStatisticsWriteTest(AbstractStatisticsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.today = self.today.decode('utf-8')  # to avoid mismatching types on asserts
        self._write_values_to_redis('java', 'processed_on', self.today, times=5)
        self._write_values_to_redis('java', 'processed_on', self._get_iso_formatted_days_before(1), times=1)
        self._write_values_to_redis('java', 'processed_on', self._get_iso_formatted_days_before(2), times=3)
        self._write_values_to_redis('java', 'processed_on', self._get_iso_formatted_days_before(3), times=20)

    def test_processed_on_for_file_type_captions(self):
        self.assertEquals(StatisticsManager().get_sample_counts_per_process_date('java').captions,
                          [self._get_iso_formatted_days_before(3),
                           self._get_iso_formatted_days_before(2),
                           self._get_iso_formatted_days_before(1),
                           self.today])

    def test_processed_on_for_file_type_counts(self):
        self.assertEquals(StatisticsManager().get_sample_counts_per_process_date('java').counts,
                          [20, 3, 1, 5])

    def test_processed_on_for_file_type_captions_affected_by_other_file_types(self):
        self._write_values_to_redis('pe', 'processed_on', self._get_iso_formatted_days_before(5), times=1)
        self.assertEquals(StatisticsManager().get_sample_counts_per_process_date('java').captions,
                          [self._get_iso_formatted_days_before(5),
                           self._get_iso_formatted_days_before(4),
                           self._get_iso_formatted_days_before(3),
                           self._get_iso_formatted_days_before(2),
                           self._get_iso_formatted_days_before(1),
                           self.today])

    def test_processed_on_for_file_type_counts_affected_by_other_file_types(self):
        """ The count list should be longer, but the number of samples for each bar of the
            chart should remain the same. """
        self._write_values_to_redis('pe', 'processed_on', self._get_iso_formatted_days_before(5), times=1)
        self.assertEquals(StatisticsManager().get_sample_counts_per_process_date('java').counts,
                          [0, 0, 20, 3, 1, 5])

    def test_processed_on_for_file_type_captions_affected_by_uploaded_on(self):
        self._write_values_to_redis('pe', 'processed_on', self._get_iso_formatted_days_before(4), times=1)
        self.assertEquals(StatisticsManager().get_sample_counts_per_process_date('java').captions,
                          [self._get_iso_formatted_days_before(4),
                           self._get_iso_formatted_days_before(3),
                           self._get_iso_formatted_days_before(2),
                           self._get_iso_formatted_days_before(1),
                           self.today])

    def test_processed_on_for_file_type_counts_affected_by_uploaded_on(self):
        """ The count list should be longer, but the number of samples for each bar of the
            chart should remain the same. """
        self._write_values_to_redis('pe', 'processed_on', self._get_iso_formatted_days_before(4), times=1)
        self.assertEquals(StatisticsManager().get_sample_counts_per_process_date('java').counts,
                          [0, 20, 3, 1, 5])


class UploadDateStatisticsWriteTest(AbstractStatisticsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.today = self.today.decode('utf-8')  # to avoid mismatching types on asserts
        self._write_values_to_redis('java', 'uploaded_on', self.today, times=7)
        self._write_values_to_redis('java', 'uploaded_on', self._get_iso_formatted_days_before(1), times=3)
        self._write_values_to_redis('java', 'uploaded_on', self._get_iso_formatted_days_before(2), times=5)

    def test_upload_on_for_file_type_captions(self):
        self.assertEquals(StatisticsManager().get_sample_counts_per_upload_date('java').captions,
                          [self._get_iso_formatted_days_before(2),
                           self._get_iso_formatted_days_before(1),
                           self.today])

    def test_upload_on_for_file_type_counts(self):
        self.assertEquals(StatisticsManager().get_sample_counts_per_upload_date('java').counts,
                          [5, 3, 7])

    def test_upload_on_for_file_type_captions_affected_by_other_file_types(self):
        self._write_values_to_redis('pe', 'uploaded_on', self._get_iso_formatted_days_before(3), times=1)
        self.assertEquals(StatisticsManager().get_sample_counts_per_upload_date('java').captions,
                          [self._get_iso_formatted_days_before(3),
                           self._get_iso_formatted_days_before(2),
                           self._get_iso_formatted_days_before(1),
                           self.today])

    def test_upload_on_for_file_type_counts_affected_by_other_file_types(self):
        """ The count list should be longer, but the number of samples for each bar of the
            chart should remain the same. """
        self._write_values_to_redis('pe', 'uploaded_on', self._get_iso_formatted_days_before(3), times=1)
        self.assertEquals(StatisticsManager().get_sample_counts_per_upload_date('java').counts,
                          [0, 5, 3, 7])
