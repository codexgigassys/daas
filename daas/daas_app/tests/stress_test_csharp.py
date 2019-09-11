import time
import logging

from .test_utils import CustomAPITestCase
from ..models import Sample
from .test_utils import CSHARP_PACK, CSHARP


class CsharpTest(CustomAPITestCase):
    #serialized_rollback = True

    def _post_teardown(self):
        pass

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert Sample.objects.count() == 0
        cls.response = cls.upload_file(CSHARP)  # replace by CSHARP_PACK
        samples = Sample.objects.all().reverse()
        # Wait until all samples are finished
        for sample in samples:
            retries = 0
            #sample = Sample.objects.get(sha1=sample.sha1)  # reload
            while not sample.finished():
                logging.info('Sleeping %s seconds, because sample #%s (sha1: %s) status is %s'
                             % (5, sample.id, sample.sha1, sample.status()))
                time.sleep(5)
                retries += 1
                if retries > 20:
                    assert False
                #sample = Sample.objects.get(sha1=sample.sha1)  # reload
            logging.info('Finished processing sample #%s (sha1: %s)! Status: %s'
                         % (sample.id, sample.sha1, sample.status()))
            #breakpoint()
            #Sample.objects.decompiled().count()

    def test_samples_created_correctly(self):
        #breakpoint()
        self.assertEqual(Sample.objects.count(), 1)

    def test_bulk_of_samples_correctly_decompiled(self):
        #breakpoint()
        self.assertEqual(Sample.objects.decompiled().count(), 1)

    def test_no_samples_timed_out(self):
        self.assertEqual(Sample.objects.timed_out().count(), 0)

    def test_no_samples_failed(self):
        self.assertEqual(Sample.objects.failed().count(), 0)
