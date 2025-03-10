import random
import string
import io
from django.conf import settings
from pyseaweed import WeedFS


def run():
    # Generate 10 random chars
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    # Use io.StringIO to avoid creating a temporary file
    random_chars = io.StringIO(random_chars)

    # Initialize WeedFS client using host and port from Django settings
    weedfs = WeedFS(settings.SEAWEEDFS_IP, settings.SEAWEEDFS_PORT)

    # Upload the file to SeaweedFS
    fid = weedfs.upload_file(stream=random_chars, name='init_file')

    # Print the file id from SeaweedFS
    print(f'File ID: {fid}')
