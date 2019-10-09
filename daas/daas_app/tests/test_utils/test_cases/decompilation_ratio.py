import time
import logging

from ...test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ....models import Sample


class DecompilationRatioTestCase(NonTransactionalLiveServerTestCase):
    @classmethod
    def setUpClass(cls, zipped_samples_path: str, timeout_per_sample: int, decompiled_samples: int,
                   timed_out_samples: int, failed_samples: int, zip_password: str = ''):
        super().setUpClass()
        cls.response = cls.upload_file(zipped_samples_path, zip_password=zip_password)
        # Expected results for tests
        cls.decompiled_samples = decompiled_samples
        cls.timed_out_samples = timed_out_samples
        cls.failed_samples = failed_samples
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
                if retries > timeout_per_sample:
                    assert False, f'Limit of {timeout_per_sample} seconds exceeded for sample: {sample})'
            logging.info(f'Finished processing sample: {sample}! Status: {sample.status()}')

    def test_samples_created_correctly(self):
        self.assertEqual(Sample.objects.count(), self.total_samples)

    def test_samples_correctly_decompiled(self):
        self.assertEqual(Sample.objects.decompiled().count(), self.decompiled_samples)

    def test_samples_timed_out(self):
        self.assertEqual(Sample.objects.timed_out().count(), self.timed_out_samples)

    def test_samples_failed(self):
        self.assertEqual(Sample.objects.failed().count(), self.failed_samples)
