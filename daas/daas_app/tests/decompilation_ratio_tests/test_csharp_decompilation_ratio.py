from ..test_utils.test_cases.decompilation_ratio import DecompilationRatioTestCase
from ..test_utils.resource_directories import CSHARP_ZIPPED_PACK


class CsharpTest(DecompilationRatioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.zipped_samples_path = CSHARP_ZIPPED_PACK
        cls.timeout_per_sample = 1200
        cls.decompiled = 114
        cls.timed_out = 1
        cls.failed, = 6
        super().setUpClass()
