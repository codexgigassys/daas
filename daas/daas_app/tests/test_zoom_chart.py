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


class SamplesPerProcessDateChartTest(StackedBarChartCustomTestCase):
    chart = samples_per_process_date_chart()

    def test_dates(self):
        self.assertEqual(self.chart['xAxis'][0]['data'], ['2018-11-29', '2018-11-30'])

    def test_start_date_for_slider(self):
        self.assertEqual(self.chart['dataZoom']['start'], 0)

    def test_legend(self):
        self.assertEqual(self.chart['legend']['data'], ['pe', 'flash'])
