import os
import shutil
import subprocess
import requests
import logging
from typing import Dict, Any, List, Optional
from requests import Response
from typing import SupportsBytes, Union
import zipfile

from .seaweed import seaweedfs


def send_result(result: Dict[str, Any], api_base_url: str) -> Response:
    logging.info(f'Seding result to API for sample with sha1={result["statistics"]["sha1"]}.')
    return requests.post(f'http://{api_base_url}/internal/api/set_result', {'result': str(result)})


def save_result(result: Dict[str, Any]) -> str:
    seaweedfs_result_id = None
    if 'source_code' in result:
        source_code = result['source_code']
        if 'file' in source_code:
            file_name = f"{result['statistics']['sha1']}_result.{source_code['extension']}"
            content = source_code.pop('file')  # Remove file content from the result dictionary
            if content is not None:
                seaweedfs_result_id = seaweedfs.upload_file(stream=content, name=file_name)
                logging.info(f'Saved result with seaweedfs_file_id: {seaweedfs_result_id}')
            else:
                logging.info('content is empty, skipping saving result')
                seaweedfs_result_id = None
        source_code['seaweedfs_result_id'] = seaweedfs_result_id  # Save seaweedFS id for the api to get the result
    return seaweedfs_result_id


def get_sample(seaweedfs_file_id: str) -> bytes:
    sample = seaweedfs.get_file(seaweedfs_file_id)
    logging.info(f'Downloaded sample with seaweedfs_file_id: {seaweedfs_file_id}')
    return sample


def remove(path: str) -> None:
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path)


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


def clean_directory(directory: str, to_keep: Optional[List[str]] = None) -> None:
    with os.scandir(directory) as entries:
        for entry in entries:
            if not to_keep or (to_keep and entry.name not in to_keep):
                if entry.is_file() or entry.is_symlink():
                    os.remove(entry.path)
                elif entry.is_dir():
                    shutil.rmtree(entry.path)


def unzip_into(zip_file_path: str, extraction_path: str) -> None:
    zip_ref = zipfile.ZipFile(zip_file_path, 'r')
    zip_ref.extractall(extraction_path)
    zip_ref.close()


def to_bytes(text: Union[SupportsBytes, bytes]) -> bytes:
    if type(text) is str:
        result = bytes(text, encoding='utf-8')
    else:
        result = bytes(text)
    return result
