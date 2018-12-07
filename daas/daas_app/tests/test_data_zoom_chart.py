from .test_utils import DataZoomChartCustomTestCase
from ..utils.charts.charts import SamplesPerUploadDateChart, SamplesPerProcessDateChart
from ..models import Sample


# It inherits from StackedBarChartCustomTestCase because they manage series in the same way.
class SamplesPerUploadDateChartTest(DataZoomChartCustomTestCase):
    def setUp(self):
        self.chart = SamplesPerUploadDateChart().updated().to_dictionary()['content']

    def test_dates(self):
        self.assertDateListEqual(self.chart['xAxis'][0]['data'], ['2018-11-29', '2018-11-30'])

    def test_start_date_for_slider(self):
        self.assertEqual(self.chart['dataZoom']['start'], 0)

    def test_legend(self):
        self.assertListEqual(self.chart['legend']['data'], ['pe', 'flash'])

    def test_samples_per_upload_date_chart_pe_series(self):
        self.assertListEqual(self.get_series('pe'), [5, 0])

    def test_samples_per_upload_date_chart_flash_series(self):
        self.assertListEqual(self.get_series('flash'), [1, 1])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.count())


class SamplesPerProcessDateChartTest(DataZoomChartCustomTestCase):
    def setUp(self):
        self.chart = SamplesPerProcessDateChart().updated().to_dictionary()['content']

    def test_dates(self):
        self.assertDateListEqual(self.chart['xAxis'][0]['data'], ['2018-11-29', '2018-11-30'])

    def test_start_date_for_slider(self):
        self.assertEqual(self.chart['dataZoom']['start'], 0)

    def test_legend(self):
        self.assertListEqual(self.chart['legend']['data'], ['pe', 'flash'])

    def test_samples_per_process_date_chart_pe_series(self):
        self.assertListEqual(self.get_series('pe'), [5, 0])

    def test_samples_per_process_date_chart_flash_series(self):
        self.assertListEqual(self.get_series('flash'), [2, 0])

    def test_all_samples_are_classified(self):
        self.assertEqual(self.get_element_count_of_multiple_series(['pe', 'flash']),
                         Sample.objects.count())
