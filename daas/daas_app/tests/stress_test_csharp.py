import time
import logging

from .test_utils import CustomTestCase
from ..models import Sample
from .test_utils import CSHARP_PACK


class CsharpTest(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.response = CustomTestCase().upload_file(CSHARP_PACK)
        samples = Sample.objects.all().reverse()
        # Wait until all samples are finished
        for sample in samples:
            sleep_seconds = 120
            sample = Sample.objects.get(sha1=sample.sha1)  # reload
            while not sample.finished():
                logging.info('Sleeping %s seconds, because sample #%s (sha1: %s) status is %s'
                             % (sleep_seconds, sample.id, sample.sha1, sample.status()))
                time.sleep(sleep_seconds)
                sleep_seconds = int(sleep_seconds*0.75) - 1
                if sleep_seconds <= 0:
                    assert False
                sample = Sample.objects.get(sha1=sample.sha1)  # reload
            logging.info('Finished processing sample #%s (sha1: %s)! Status: %s'
                         % (sample.id, sample.sha1, sample.status()))

    def test_redirection(self):
        self.assertEqual(self.response.url, '/index')

    def test_samples_created_correctly(self):
        self.assertEqual(Sample.objects.count(), 118)

    def test_bulk_of_samples_correctly_decompiled(self):
        self.assertEqual(Sample.objects.decompiled().count(), 118)

    def test_no_samples_timed_out(self):
        self.assertEqual(Sample.objects.timed_out().count(), 0)

    def test_no_samples_failed(self):
        self.assertEqual(Sample.objects.failed().count(), 0)
