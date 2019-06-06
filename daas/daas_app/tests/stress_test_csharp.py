from .test_utils import CustomTestCase
from ..models import Sample
from .test_utils import CSHARP_PACK
import time


class CsharpTest(CustomTestCase):
    def setUp(self):
        self.response = self.upload_file(CSHARP_PACK)
        samples = Sample.objects.all()
        # Wait until all samples are finished
        for sample in samples:
            while not sample.finished():
                time.sleep(1)

    def test_redirection(self):
        self.assertEqual(response.url, '/index')

    def test_samples_created_correctly(self):
        self.assertEqual(Sample.objects.count(), 118)

    def test_bulk_of_samples_correctly_decompiled(self):
        self.assertEqual(Sample.objects.decompiled().count(), 118)

    def test_no_samples_timed_out(self):
        self.assertEqual(Sample.objects.timed_out().count(), 0)

    def test_no_samples_failed(self):
        self.assertEqual(Sample.objects.failed().count(), 0)
