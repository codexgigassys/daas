import time
import os
import shutil
import subprocess
import requests


def get_port():
    return 8001


def send_result(result, port=get_port()):
    url = f"http://api:{port}/set_result"
    payload = {'result': str(result)}
    response = requests.post(url, payload)
    return response


def get_sample(sample_id, port=get_port()):
    return requests.get(f"http://api:{port}/download_sample/%s" % sample_id).content


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
