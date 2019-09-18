from ..test_utils.test_cases.charts import StackedBarChartCustomTestCase
from ...models import Sample
from ...utils.charts.charts import SamplesPerSizeChart, SamplesPerElapsedTimeChart


class SamplesPerSizeChartTest(StackedBarChartCustomTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.chart = SamplesPerSizeChart().updated().content

    def test_samples_per_size_chart_pe_series(self):
        self.assertEqual(self.get_series('pe'), [1, 1, 0, 0, 0, 0, 1, 2])

    def test_samples_per_size_chart_flash_series(self):
        self.assertEqual(self.get_series('flash'), [0, 0, 0, 1, 0, 0, 0, 1])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.count())


class SamplesPerElapsedTimeChartTest(StackedBarChartCustomTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.chart = SamplesPerElapsedTimeChart().updated().content

    def test_samples_per_size_chart_pe_series(self):
        self.assertEqual(self.get_series('pe'), [0, 0, 0, 0, 1, 2, 2, 0, 0])

    def test_samples_per_size_chart_flash_series(self):
        self.assertEqual(self.get_series('flash'), [0, 0, 0, 0, 0, 0, 1, 1, 0])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']), Sample.objects.count())
