from typing import List, Optional

from ....utils.task_manager import TaskManager
from ....models import Sample


class SampleSubmitMixin:
    def _submit_samples(self, samples: List[Sample], force_reprocess: bool = False) -> None:
        for sample in samples:
            self._submit_sample(sample, force_reprocess)

    def _submit_sample(self, sample: Sample, force_reprocess: bool = False) -> None:
        TaskManager().submit_sample(sample, force_reprocess)

    def _get_sample(self, sha1: str) -> Optional[List[Sample]]:
        try:
            sample = Sample.objects.get(sha1=sha1)
        except Sample.DoesNotExist:
            sample = None
        return sample
