import logging
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from typing import Iterable, Optional

from .sample_submit import SampleSubmitMixin
from ....models import Sample


# from ...utils.callback_manager import CallbackManager


class ReprocessMixin(LoginRequiredMixin, PermissionRequiredMixin, SampleSubmitMixin):
    permission_required = 'daas_app.upload_sample_permission'

    def reprocess(self, samples: Iterable[Sample], force_reprocess: bool = False, callback: Optional[str] = None) -> None:
        logging.info(f'Reprocess API. {samples=}. {force_reprocess=}. {callback=}.')
        for sample in samples:
            if sample.has_content:
                logging.debug(f'Reprocessing sample: {sample.sha1=}')
                self._submit_sample(sample, force_reprocess=True)

        # if not force_reprocess:
        # Return data for samples processed with the latest decompiler.
        #    for sample in samples.processed_with_current_decompiler_version():
        #        CallbackManager().call(callback, sample.sha1)
        #    samples = samples.processed_with_old_decompiler_version()

        # Reprocess and add a callback for samples processed with old decompilers.
        # for sample in samples:
        #    CallbackManager().add_url(callback, sample.sha1)
        #    reprocess(sample, force_reprocess=force_reprocess)
