from .test_utils import StackedBarChartCustomTestCase
from ..views import samples_per_size_chart, samples_per_elapsed_time_chart
from ..models import Sample


class SamplesPerSizeChartTest(StackedBarChartCustomTestCase):
    def setUp(self):
        self.chart = samples_per_size_chart()

    def test_samples_per_size_chart_pe_series(self):
        self.assertEqual(self.get_series('pe'), [1, 1, 0, 0, 0, 0, 1, 2])

    def test_samples_per_size_chart_flash_series(self):
        self.assertEqual(self.get_series('flash'), [0, 0, 0, 1, 0, 0, 0, 1])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.count())


class SamplesPerElapsedTimeChartTest(StackedBarChartCustomTestCase):
    def setUp(self):
        self.chart = samples_per_elapsed_time_chart()

    def test_samples_per_size_chart_pe_series(self):
        self.assertEqual(self.get_series('pe'), [0, 0, 0, 0, 1, 2, 2, 0])

    def test_samples_per_size_chart_flash_series(self):
        self.assertEqual(self.get_series('flash'), [0, 0, 0, 0, 0, 0, 0, 1])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.decompiled().count())

