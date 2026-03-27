#!/usr/bin/env python3
"""
Integration test for verifying that sample upload + processing + deletion
does not leak files in GridFS.
"""

import hashlib
import io
import os
import sys
import time
from pathlib import Path
from typing import Optional

import django
import requests
from pymongo import MongoClient

from daas_app.models import Sample  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
os.chdir(str(_REPO_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daas.settings")
django.setup()

DEFAULT_BASE_URL = "http://localhost:8001"


def get_gridfs_file_count() -> int:
    client = MongoClient(
        host=os.environ.get("MONGO_HOST", "mongo"),
        port=int(os.environ.get("MONGO_PORT", "27017")),
        serverSelectionTimeoutMS=10000,
    )
    db = client[os.environ.get("MONGO_DB", "daas_files")]
    count = db["fs.files"].count_documents({})
    print(f"GridFS file count: {count}")
    return count


class GridFSStorageLeakIntegrationTest:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.environ.get("DAASTEST_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.session = requests.Session()

    def upload_file(self, file_path: str) -> Optional[tuple[str, bool]]:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return None

        with open(file_path, "rb") as f:
            content = f.read()
            sha1_hash = hashlib.sha1(content).hexdigest()

        files = {
            "file": (
                os.path.basename(file_path),
                io.BytesIO(content),
                "application/octet-stream",
            )
        }
        data = {"sha1": sha1_hash}
        response = self.session.post(f"{self.base_url}/api/upload/", files=files, data=data)
        if response.status_code == 202:
            return (sha1_hash, False)
        if response.status_code == 400:
            check = self.session.get(f"{self.base_url}/api/get_sample_from_hash/{sha1_hash}")
            if check.status_code == 200:
                return (sha1_hash, True)
        return None

    def wait_for_processing(self, sha1_hash: str, max_wait_time: int = 300, poll_interval: int = 5) -> bool:
        start_time = time.time()
        terminal_statuses = {"DONE", "FAILED", "TIMED_OUT", "CANCELLED"}

        while time.time() - start_time < max_wait_time:
            response = self.session.get(f"{self.base_url}/api/get_sample_from_hash/{sha1_hash}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status", "UNKNOWN") in terminal_statuses:
                    return True
            time.sleep(poll_interval)
        return False

    def delete_sample_from_django(self, sha1_hash: str) -> bool:
        try:
            sample = Sample.objects.get(sha1=sha1_hash)
        except Sample.DoesNotExist:
            return False
        sample.delete()
        return True

    def run_test(self, sample_path: str) -> bool:
        initial_count = get_gridfs_file_count()
        upload_result = self.upload_file(sample_path)
        if not upload_result:
            return False
        sha1_hash, already_existed = upload_result

        if not already_existed and not self.wait_for_processing(sha1_hash):
            return False
        if not self.delete_sample_from_django(sha1_hash):
            return False

        time.sleep(5)
        final_count = get_gridfs_file_count()
        return initial_count == final_count


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 tests/test_seaweed_storage_leak_integration.py /path/to/sample.bin")
        sys.exit(1)

    test = GridFSStorageLeakIntegrationTest()
    success = test.run_test(sys.argv[1])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
