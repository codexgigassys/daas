import time
import logging

from .test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ..models import Sample
from .test_utils.resource_directories import CSHARP_SAMPLE, CSHARP_ZIPPED_PACK


class CsharpTest(NonTransactionalLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert Sample.objects.count() == 0
        cls.response = cls.upload_file(CSHARP_SAMPLE)  # fixme: replace by CSHARP_ZIPPED_PACK
        samples = Sample.objects.all().reverse()
        # Wait until all samples are decompiled
        for sample in samples:
            retries = 0
            while not sample.finished():
                logging.info('Sleeping %s seconds, because sample #%s (sha1: %s) status is %s'
                             % (5, sample.id, sample.sha1, sample.status()))
                time.sleep(5)
                retries += 1
                if retries > 20:
                    assert False
            logging.info('Finished processing sample #%s (sha1: %s)! Status: %s'
                         % (sample.id, sample.sha1, sample.status()))

    def test_samples_created_correctly(self):
        self.assertEqual(Sample.objects.count(), 1)

    def test_bulk_of_samples_correctly_decompiled(self):
        self.assertEqual(Sample.objects.decompiled().count(), 1)

    def test_no_samples_timed_out(self):
        self.assertEqual(Sample.objects.timed_out().count(), 0)

    def test_no_samples_failed(self):
        self.assertEqual(Sample.objects.failed().count(), 0)


class CsharpTest2(NonTransactionalLiveServerTestCase):
    def test_samples_created_correctly(self):
        self.assertEqual(Sample.objects.count(), 0, 'DATABSE SHOULD BE EMPTY')
