from ..test_utils.test_cases.decompilation_ratio import DecompilationRatioTestCase
from ..test_utils.resource_directories import FLASH_ZIPPED_PACK


class FlashTest(DecompilationRatioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.zipped_samples_path = FLASH_ZIPPED_PACK
        cls.timeout_per_sample = 1200
        cls.decompiled = 100
        cls.timed_out = 0
        cls.failed = 0
        cls.zip_password = 'ASDF1234'
        super().setUpClass()
