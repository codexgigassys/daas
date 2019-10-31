from ..test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ..test_utils.test_cases.decompilation_ratio import DecompilationRatioTestCaseMixin
from ..test_utils.resource_directories import CSHARP_ZIPPED_PACK


class CsharpTest(NonTransactionalLiveServerTestCase, DecompilationRatioTestCaseMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        super().postSetUpClass(zipped_samples_path=CSHARP_ZIPPED_PACK,
                               timeout_per_sample=1200,
                               decompiled_samples=114,
                               failed_samples=6,
                               zip_password='codex')
