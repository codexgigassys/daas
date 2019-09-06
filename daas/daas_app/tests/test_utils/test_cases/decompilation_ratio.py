import time
import logging

from ...test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ....models import Sample


class DecompilationRatioTestCase(NonTransactionalLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        """ You need to provide:
                cls.zipped_samples_path
                cls.timeout_per_sample
                cls.decompiled
                cls.timed_out
                cls.failed,
            and call super().setUpClass() if you want to add more behaviour to it. """
        super().setUpClass()
        cls.response = cls.upload_file(cls.zipped_samples_path)
        cls.total_samples = cls.decompiled_samples + cls.timed_out_samples + cls.failed_samples
        samples = Sample.objects.all().reverse()
        # Wait until all samples are decompiled
        for sample in samples:
            retries = 0
            while not sample.finished():
                if retries % 10 == 0:
                    logging.info(f'Sample {sample} status is {sample.status()}. Sleeping...')
                time.sleep(1)
                retries += 1
                if retries > cls.timeout_per_sample:
                    assert False, f'Limit of {cls.timeout_per_sample} seconds exceeded for sample: {sample})'
            logging.info(f'Finished processing sample: {sample}! Status: {sample.status()}')

    def test_samples_created_correctly(self):
        self.assertEqual(Sample.objects.count(), self.total_samples)

    def test_samples_correctly_decompiled(self):
        self.assertEqual(Sample.objects.decompiled().count(), self.decompiled_samples)

    def test_samples_timed_out(self):
        self.assertEqual(Sample.objects.timed_out().count(), self.timed_out_samples)

    def test_samples_failed(self):
        self.assertEqual(Sample.objects.failed().count(), self.failed_samples)
