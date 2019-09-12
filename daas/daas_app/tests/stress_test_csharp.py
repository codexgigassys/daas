import time
import logging

from .test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ..models import Sample
from .test_utils.resource_directories import CSHARP_ZIPPED_PACK


class CsharpTest(NonTransactionalLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.response = cls.upload_file(CSHARP_ZIPPED_PACK)
        samples = Sample.objects.all().reverse()
        # Wait until all samples are decompiled
        for sample in samples:
            retries = 0
            while not sample.finished():
                logging.info(f'Sleeping 5 seconds, because sample {sample} status is {sample.status()}')
                time.sleep(5)
                retries += 1
                if retries > 50:
                    assert False, f'Limit of 50 retries exceeded for sample: {sample})'
            logging.info(f'Finished processing sample: {sample}! Status: {sample.status()}')

    def test_samples_created_correctly(self):
        self.assertEqual(Sample.objects.count(), 1)

    def test_bulk_of_samples_correctly_decompiled(self):
        self.assertEqual(Sample.objects.decompiled().count(), 1)

    def test_no_samples_timed_out(self):
        self.assertEqual(Sample.objects.timed_out().count(), 0)

    def test_no_samples_failed(self):
        self.assertEqual(Sample.objects.failed().count(), 0)
