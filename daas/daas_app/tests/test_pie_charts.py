from .test_utils import PieChartCustomTestCase
from ..views import samples_per_type_chart, samples_per_decompilation_status_chart, samples_per_upload_date_chart, samples_per_process_date_chart
from ..models import Sample


class SamplesPerTypeChartTest(PieChartCustomTestCase):
    chart = samples_per_type_chart()

    def test_samples_per_type_chart_pe(self):
        self.assertEqual(self.get_samples_of('pe'), 5)

    def test_samples_per_type_chart_flash(self):
        self.assertEqual(self.get_samples_of('flash'), 2)

    def test_all_samples_classified(self):
        self.assertEqual(self.get_samples_of('pe') + self.get_samples_of('flash'),
                         Sample.objects.count())


class SamplesPerDecompilationStatusChartTest(PieChartCustomTestCase):
    chart = samples_per_decompilation_status_chart('pe')

    def test_samples_per_decompilation_status_decompiled(self):
        self.assertEqual(self.get_samples_of('Decompiled'), 5)

    def test_samples_per_decompilation_status_timedout(self):
        self.assertEqual(self.get_samples_of('Time out'), 0)

    def test_samples_per_decompilation_status_failed(self):
        self.assertEqual(self.get_samples_of('Failed'), 0)

    def test_all_samples_classified(self):
        self.assertEqual(self.get_samples_of('Decompiled') + self.get_samples_of('Time out') + self.get_samples_of('Failed'),
                         Sample.objects.count())
