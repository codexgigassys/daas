from ..test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ..test_utils.test_cases.decompilation_ratio import DecompilationRatioTestCaseMixin
from ..test_utils.resource_directories import JAVA_ZIPPED_PACK


class JavaTest(NonTransactionalLiveServerTestCase, DecompilationRatioTestCaseMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        super().postSetUpClass(zipped_samples_path=JAVA_ZIPPED_PACK,
                               timeout_per_sample=1200,
                               decompiled_samples=84,
                               failed_samples=0,
                               zip_password='codex')
