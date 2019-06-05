from .test_utils import PieChartCustomTestCase
from ..utils.charts.charts import SamplesPerTypeChart, SamplesPerDecompilationStatusChart
from ..models import Sample


class SamplesPerTypeChartTest(PieChartCustomTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.chart = SamplesPerTypeChart().updated().content

    def test_samples_per_type_chart_pe(self):
        self.assertEqual(self.get_samples_of('pe'), 5)

    def test_samples_per_type_chart_flash(self):
        self.assertEqual(self.get_samples_of('flash'), 2)

    def test_all_samples_classified(self):
        self.assertEqual(self.get_samples_of('pe') + self.get_samples_of('flash'),
                         Sample.objects.count())


class SamplesPerDecompilationStatusPEChartTest(PieChartCustomTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.chart = SamplesPerDecompilationStatusChart('pe').updated().content

    def test_samples_per_decompilation_status_decompiled(self):
        self.assertEqual(self.get_samples_of('Decompiled'), 5)

    def test_samples_per_decompilation_status_timedout(self):
        self.assertEqual(self.get_samples_of('Time out'), 0)

    def test_samples_per_decompilation_status_failed(self):
        self.assertEqual(self.get_samples_of('Failed'), 0)

    def test_all_samples_classified(self):
        self.assertEqual(self.get_samples_of('Decompiled') + self.get_samples_of('Time out') + self.get_samples_of('Failed'),
                         Sample.objects.classify_by_file_type()['pe'].count())


class SamplesPerDecompilationStatusFlashChartTest(PieChartCustomTestCase):
    def setUpTestData(self):
        self.chart = SamplesPerDecompilationStatusChart('flash').updated().content

    def test_samples_per_decompilation_status_decompiled(self):
        self.assertEqual(self.get_samples_of('Decompiled'), 1)

    def test_samples_per_decompilation_status_timedout(self):
        self.assertEqual(self.get_samples_of('Time out'), 1)

    def test_samples_per_decompilation_status_failed(self):
        self.assertEqual(self.get_samples_of('Failed'), 0)

    def test_all_samples_classified(self):
        self.assertEqual(self.get_samples_of('Decompiled') + self.get_samples_of('Time out') + self.get_samples_of('Failed'),
                         Sample.objects.classify_by_file_type()['flash'].count())
