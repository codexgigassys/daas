import logging
from typing import Iterable, Optional

from .sample_submit import SampleSubmitMixin
from ....models import Sample
from ....utils.callback_manager import CallbackManager


class ReprocessMixin(SampleSubmitMixin):
    def reprocess(self, samples: Iterable[Sample], force_reprocess: bool = False, callback: Optional[str] = None) -> int:
        logging.info(f'Reprocess API. {samples=}. {force_reprocess=}. {callback=}.')
        submitted_samples = self._submit_samples(samples, force_reprocess=force_reprocess)

        # Add a callback for samples processed with old decompilers.
        for sample in samples:
            CallbackManager().add_url(sample.sha1, callback)

        return submitted_samples
