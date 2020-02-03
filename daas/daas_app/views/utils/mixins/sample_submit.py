from typing import Iterable, List, Optional

from ....utils.task_manager import TaskManager
from ....models import Sample


class SampleSubmitMixin:
    def _submit_samples(self, samples: Iterable[Sample], force_reprocess: bool = False) -> int:
        submitted_samples = 0
        for sample in samples:
            if self._submit_sample(sample, force_reprocess):
                submitted_samples += 1
        return submitted_samples

    def _submit_sample(self, sample: Sample, force_reprocess: bool = False) -> bool:
        return TaskManager().submit_sample(sample, force_process=force_reprocess)

    def _get_sample(self, sha1: str) -> Optional[List[Sample]]:
        try:
            sample = Sample.objects.get(sha1=sha1)
        except Sample.DoesNotExist:
            sample = None
        return sample
