from .test_utils import StackedBarChartCustomTestCase
from ..views import samples_per_upload_date_chart, samples_per_process_date_chart
from ..models import Sample


class SamplesPerUploadDateChartTest(StackedBarChartCustomTestCase):
    chart = samples_per_upload_date_chart()

    def test_dates(self):
        self.assertEqual(self.chart['xAxis'][0]['data'], ['2018-11-29', '2018-11-30'])

    def test_start_date_for_slider(self):
        self.assertEqual(self.chart['dataZoom']['start'], 0)

    def test_legend(self):
        self.assertEqual(self.chart['legend']['data'], ['pe', 'flash'])

    def test_samples_per_size_chart_pe_series(self):
        self.assertEqual(self.get_series('pe'), [5, 0])

    def test_samples_per_size_chart_flash_series(self):
        self.assertEqual(self.get_series('flash'), [1, 1])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.count())


class SamplesPerProcessDateChartTest(StackedBarChartCustomTestCase):
    chart = samples_per_process_date_chart()

    def test_dates(self):
        self.assertEqual(self.chart['xAxis'][0]['data'], ['2018-11-29', '2018-11-30'])

    def test_start_date_for_slider(self):
        self.assertEqual(self.chart['dataZoom']['start'], 0)

    def test_legend(self):
        self.assertEqual(self.chart['legend']['data'], ['pe', 'flash'])

    def test_samples_per_size_chart_pe_series(self):
        self.assertEqual(self.get_series('pe'), [5, 0])

    def test_samples_per_size_chart_flash_series(self):
        self.assertEqual(self.get_series('flash'), [1, 1])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.count())
