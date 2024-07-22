from ..test_utils.test_cases.generic import NonTransactionalLiveServerTestCase
from ..test_utils.test_cases.decompilation_ratio import DecompilationRatioTestCaseMixin
from ..test_utils.resource_directories import FLASH_ZIPPED_PACK


class FlashTest(NonTransactionalLiveServerTestCase, DecompilationRatioTestCaseMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        super().postSetUpClass(zipped_samples_path=FLASH_ZIPPED_PACK,
                               timeout_per_sample=1200,
                               decompiled_samples=95,
                               failed_samples=4,
                               zip_password='codex')
