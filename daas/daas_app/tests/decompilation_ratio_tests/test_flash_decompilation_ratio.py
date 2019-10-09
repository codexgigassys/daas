from ..test_utils.test_cases.decompilation_ratio import DecompilationRatioTestCase
from ..test_utils.resource_directories import FLASH_ZIPPED_PACK


class FlashTest(DecompilationRatioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass(zipped_samples_path=FLASH_ZIPPED_PACK,
                           timeout_per_sample=1200,
                           decompiled_samples=100,
                           timed_out_samples=0,
                           failed_samples=0,
                           zip_password='ASDF1234')
