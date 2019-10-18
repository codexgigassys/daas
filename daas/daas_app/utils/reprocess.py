import logging

from ..uploaded_files import create_and_update_file


def reprocess(sample, force_reprocess=False):
    # If we didn't save the sample, we have no way to decompile it again using this function
    if sample.content_saved():
        logging.debug(f'Reprocessing sample: {sample.id}')
        create_and_update_file(sample.name, sample.data, force_reprocess=force_reprocess)
    else:
        # It's not necessary to return a proper error here, because the URL will not be accessible via GUI
        # if the sample is not saved.
        logging.error('It was not possible to reprocess sample {sample.id} because it was not saved.')
