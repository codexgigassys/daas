from ..test_utils.test_cases.decompilation_ratio import DecompilationRatioTestCase
from ..test_utils.resource_directories import CSHARP_ZIPPED_PACK


class CsharpTest(DecompilationRatioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass(zipped_samples_path=CSHARP_ZIPPED_PACK,
                           timeout_per_sample=1200,
                           decompiled_samples=114,
                           timed_out_samples=1,
                           failed_samples=6,
                           zip_password='codex')
