import os
import shutil
import subprocess
import requests


class DaaSAPIConnector:
    def __init__(self, api_base_url):
        self.base_url = api_base_url

    def send_result(self, result):
        return requests.post(f'http://{self.base_url}/internal/api/set_result', {'result': str(result)})

    def get_sample(self, sample_id):
        return requests.get(f'http://{self.base_url}/internal/api/download_sample/{sample_id}').content


def has_a_non_empty_file(base_path):
    for path, subdirs, files in os.walk(base_path):
        for name in files:
            file_path = os.path.join(path, name)
            if file_is_not_empty(file_path):
                return True
    return False


def file_is_not_empty(file_path):
    return subprocess.check_output(['du', '-sh', file_path]).split()[0] != '0'


def shutil_compression_algorithm_to_extnesion(shutil_algorithm):
    shutil_algorithm_to_extension = {'zip': 'zip', 'gztar': 'tar.gz', 'bztar': 'tar.bz2', 'xztar': 'tar.xz'}
    return shutil_algorithm_to_extension[shutil_algorithm]


def clean_directory(directory: str) -> None:
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file() or entry.is_symlink():
                os.remove(entry.path)
            elif entry.is_dir():
                shutil.rmtree(entry.path)
