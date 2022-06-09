import os
import shutil
import subprocess
import requests
import logging
from pyseaweed import WeedFS
from typing import Dict, Any
from requests import Response


seaweedfs = WeedFS('seaweedfs_master', 9333)

# Comment the line above and uncomment the line below to work with k8s cluster

#seaweedfs = WeedFS('seaweedfs-master', 9333)


def send_result(result: Dict[str, Any], api_base_url: str) -> Response:
    logging.info(f'Seding result to API for sample with sha1={result["statistics"]["sha1"]}.')
    return requests.post(f'http://{api_base_url}/internal/api/set_result', {'result': str(result)})


def get_sample(seaweedfs_file_id: str) -> bytes:
    # FIXME: use seaweed id instead
    sample = seaweedfs.get_file(seaweedfs_file_id)
    logging.info(f'Downloaded sample with seaweedfs_file_id: {seaweedfs_file_id}')
    return sample


def has_a_non_empty_file(base_path: str) -> bool:
    for path, subdirs, files in os.walk(base_path):
        for name in files:
            file_path = os.path.join(path, name)
            if file_is_not_empty(file_path):
                return True
    return False


def file_is_not_empty(file_path: str) -> bool:
    return subprocess.check_output(['du', '-sh', file_path]).split()[0] != '0'


def shutil_compression_algorithm_to_extnesion(shutil_algorithm: str) -> str:
    shutil_algorithm_to_extension = {'zip': 'zip', 'gztar': 'tar.gz', 'bztar': 'tar.bz2', 'xztar': 'tar.xz'}
    return shutil_algorithm_to_extension[shutil_algorithm]


def clean_directory(directory: str) -> None:
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file() or entry.is_symlink():
                os.remove(entry.path)
            elif entry.is_dir():
                shutil.rmtree(entry.path)
