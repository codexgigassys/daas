from ..test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ..test_utils.test_cases.decompilation_ratio import DecompilationRatioTestCaseMixin
from ..test_utils.resource_directories import APK_ZIPPED_PACK


class APKTest(NonTransactionalLiveServerTestCase, DecompilationRatioTestCaseMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        super().postSetUpClass(zipped_samples_path=APK_ZIPPED_PACK,
                               timeout_per_sample=1500,
                               decompiled_samples=67,
                               failed_samples=0,
                               zip_password='codex')
