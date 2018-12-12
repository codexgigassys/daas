import logging

from .upload_file import upload_file


def reprocess(sample):
    # If we didn't save the sample, we have no way to decompile it again using this function
    if sample.content_saved():
        logging.debug('Reprocessing sample: %s' % sample.id)
        upload_file(sample.name, sample.data.tobytes(), reprocessing=True)
    else:
        # It's not necessary to return a proper error here, because the URL will not be accessible via GUI
        # if the sample is not saved.
        logging.error('It was not possible to reprocess sample %s because it was not saved.' % sample.id)
