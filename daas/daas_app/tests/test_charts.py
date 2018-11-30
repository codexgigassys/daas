from .test_utils import ChartCustomTestCase
from ..utils.charts import bar_chart_json_generator, data_zoom_chart_json_generator, pie_chart_json_generator
from ..views import samples_per_size_chart, samples_per_elapsed_time_chart, samples_per_type_chart, samples_per_decompilation_status_chart, samples_per_upload_date_chart, samples_per_process_date_chart
from ..models import Sample


class SamplesPerSizeChartTest(ChartCustomTestCase):
    chart = samples_per_size_chart()

    def test_samples_per_size_chart_pe_series(self):
        self.assertEqual(self.get_series('pe'), [1, 1, 0, 0, 0, 0, 1, 2])

    def test_samples_per_size_chart_flash_series(self):
        self.assertEqual(self.get_series('flash'), [0, 0, 0, 1, 0, 0, 0, 1])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.count())


class SamplesPerElapsedTimeChartTest(ChartCustomTestCase):
    chart = samples_per_elapsed_time_chart()

    def test_samples_per_size_chart_pe_series(self):
        self.assertEqual(self.get_series('pe'), [0, 0, 0, 0, 1, 2, 2, 0])

    def test_samples_per_size_chart_flash_series(self):
        self.assertEqual(self.get_series('flash'), [0, 0, 0, 0, 0, 0, 0, 1])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.decompiled().count())
