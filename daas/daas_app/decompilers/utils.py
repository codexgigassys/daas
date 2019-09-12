import time
import os
import shutil
import subprocess
import requests


class DaaSAPIConnector:
    def __init__(self, api_base_url):
        self.base_url = api_base_url

    def send_result(self, result):
        return requests.post(f'http://{self.base_url}/set_result',
                             {'result': str(result)})

    def get_sample(self, sample_id):
        return requests.get(f'http://{self.base_url}/download_sample/{sample_id}').content


def remove_directory(path):
    remove(path, remove_function=shutil.rmtree)


def remove_file(path):
    remove(path, remove_function=os.remove)


def remove(path, remove_function):
    for i in range(4):
        try:
            remove_function(path)
        except OSError:
            # Sometimes a file descriptor remains open, so we wait and try again
            time.sleep(int(i) + 1)


def has_a_non_empty_file(base_path):
    for path, subdirs, files in os.walk(base_path):
        for name in files:
            file_path = os.path.join(path, name)
            if file_is_not_empty(file_path):
                return True
    return False


def file_is_not_empty(file_path):
    return subprocess.check_output(['du', '-sh', file_path]).split()[0] != '0'
