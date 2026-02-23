#!/usr/bin/env python3
"""
Integration test for verifying that sample upload + processing + deletion
does not leak files in SeaweedFS.

Flow:
- Count total files stored in SeaweedFS.
- Upload a sample through the public upload API.
- Wait until the sample is fully processed (terminal status).
- Delete the corresponding Sample from Django (which should also delete
  the underlying SeaweedFS file(s)).
- Count total files in SeaweedFS again and assert it matches the initial count.

Usage:
    python3 tests/test_seaweed_storage_leak_integration.py /path/to/sample.bin

This script assumes:
- DaaS API is reachable at http://localhost:8081 (override with DAASTEST_BASE_URL).
- SeaweedFS master is reachable at seaweedfs-master:9333
  (override with SEAWEEDFS_IP / SEAWEEDFS_PORT env vars).
- It is executed in the same environment/container as the Django app so it can
  import the Django settings module and ORM.
"""

import hashlib
import json
import os
import io
import sys
import time
from pathlib import Path
from typing import Optional

import requests


# Ensure repo root (parent of daas_app/) is on path so daas and daas_app are importable
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
os.chdir(str(_REPO_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daas.settings")

import django

django.setup()

from daas_app.models import Sample  # noqa: E402


DEFAULT_BASE_URL = "http://localhost:8001"


def get_seaweed_master_host() -> str:
    return os.environ.get("SEAWEEDFS_IP", "seaweedfs-master")


def get_seaweed_master_port() -> int:
    return int(os.environ.get("SEAWEEDFS_PORT", "9333"))


def _extract_live_file_count_from_vol_status(vol_status_json: dict) -> int:
    """
    Extract an approximate number of live files from SeaweedFS /vol/status output.

    Structure: Volumes.DataCenters.<dc>.<rack>.<server> = list of volume objects,
    each with FileCount/DeleteCount.

    SeaweedFS FileCount is cumulative over writes. To detect leaks, we compare:
        live_count ~= FileCount - DeleteCount
    """
    total = 0
    volumes_root = vol_status_json.get("Volumes") or vol_status_json.get("volumes") or {}
    data_centers = volumes_root.get("DataCenters") or volumes_root.get("dataCenters") or {}

    for _dc_name, racks in data_centers.items():
        if not isinstance(racks, dict):
            continue
        for _rack_name, servers in racks.items():
            if not isinstance(servers, dict):
                continue
            for _server_id, vol_list in servers.items():
                if not isinstance(vol_list, list):
                    continue
                for vol in vol_list:
                    if isinstance(vol, dict):
                        file_count = (
                            vol.get("FileCount")
                            or vol.get("fileCount")
                            or vol.get("file_count")
                            or 0
                        )
                        delete_count = (
                            vol.get("DeleteCount")
                            or vol.get("deleteCount")
                            or vol.get("delete_count")
                            or 0
                        )
                        total += int(file_count) - int(delete_count)

    return total


def get_seaweed_file_count() -> int:
    """Return an approximate live file count stored in SeaweedFS."""
    host = get_seaweed_master_host()
    port = get_seaweed_master_port()
    url = f"http://{host}:{port}/vol/status"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to query SeaweedFS status from {url}: {e}")
        raise

    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        print(f"❌ Failed to decode SeaweedFS status JSON: {e}")
        raise

    total = _extract_live_file_count_from_vol_status(data)
    print(f"📦 SeaweedFS reported live file count: {total}")
    return total


def _normalize_base_url(url: str) -> str:
    """Strip trailing slash so joining with '/api/...' never produces double slashes."""
    return url.rstrip("/")


class SeaweedStorageLeakIntegrationTest:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = _normalize_base_url(
            base_url or os.environ.get("DAASTEST_BASE_URL", DEFAULT_BASE_URL)
        )
        self.session = requests.Session()

    # --------------------------
    # Step 1: Upload via API
    # --------------------------
    def upload_file(self, file_path: str) -> Optional[tuple[str, bool]]:
        """Upload a file to DaaS. Returns (sha1_hash, already_existed) or None on failure."""
        if not os.path.exists(file_path):
            print(f"❌ Error: File not found: {file_path}")
            return None

        print(f"📤 Uploading file: {file_path}")

        with open(file_path, "rb") as f:
            content = f.read()
            sha1_hash = hashlib.sha1(content).hexdigest()

        print(f"🔍 File SHA1: {sha1_hash}")

        # Send file as a file-like object so the server receives it correctly
        files = {
            "file": (
                os.path.basename(file_path),
                io.BytesIO(content),
                "application/octet-stream",
            )
        }
        data = {"sha1": sha1_hash}

        try:
            response = self.session.post(f"{self.base_url}/api/upload/", files=files, data=data)
            if response.status_code == 202:
                print("✅ Upload successful (202 Accepted)")
                return (sha1_hash, False)
            if response.status_code == 400:
                # API returns 400 when sample already exists; we can still run the test (delete it)
                check = self.session.get(
                    f"{self.base_url}/api/get_sample_from_hash/{sha1_hash}"
                )
                if check.status_code == 200:
                    print("⚠️ Sample already exists (400); continuing to delete.")
                    return (sha1_hash, True)
                print(f"❌ Upload failed with status 400: {response.text or '(no body)'}")
                return None
            print(f"❌ Upload failed with status {response.status_code}: {response.text}")
            return None
        except requests.RequestException as e:
            print(f"❌ Upload request failed: {e}")
            return None

    # --------------------------
    # Step 2: Wait for processing
    # --------------------------
    def wait_for_processing(
        self,
        sha1_hash: str,
        max_wait_time: int = 300,
        poll_interval: int = 5,
    ) -> bool:
        """
        Wait until the sample reaches a terminal status.

        This is used as a proxy for "no tasks pending" for this sample.
        """
        print(f"⏳ Waiting for processing to complete (max {max_wait_time}s)...")

        start_time = time.time()
        terminal_statuses = {"DONE", "FAILED", "TIMED_OUT", "CANCELLED"}

        while time.time() - start_time < max_wait_time:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/get_sample_from_hash/{sha1_hash}"
                )
            except requests.RequestException as e:
                print(f"⚠️ Request failed: {e}")
                time.sleep(poll_interval)
                continue

            if response.status_code == 200:
                data = response.json()
                # GetSampleFromHashAPIView returns SampleSerializer data directly
                # SampleSerializer includes 'status' field which returns SampleStatus enum name
                sample_status = data.get("status", "UNKNOWN")
                print(f"📊 Sample status: {sample_status}")

                if sample_status in terminal_statuses:
                    print(f"✅ Processing completed with status: {sample_status}")
                    return True
            elif response.status_code == 404:
                print("⏳ Sample not found yet, still processing...")
            else:
                print(f"⚠️ Unexpected response {response.status_code}: {response.text}")

            time.sleep(poll_interval)

        print(f"⏰ Timeout reached after {max_wait_time}s")
        return False

    # --------------------------
    # Step 3: Delete Sample via ORM
    # --------------------------
    def delete_sample_from_django(self, sha1_hash: str) -> bool:
        """
        Delete the Sample corresponding to the given SHA1 hash using Django ORM.

        This triggers Sample.delete(), which is responsible for removing
        the associated SeaweedFS file.
        """
        print(f"🗑  Deleting Sample with sha1={sha1_hash} via Django ORM...")

        try:
            sample = Sample.objects.get(sha1=sha1_hash)
        except Sample.DoesNotExist:
            print(f"⚠️ No Sample found with sha1={sha1_hash}")
            return False

        try:
            sample.delete()
            print("✅ Sample deleted from Django (and SeaweedFS cleanup triggered).")
            return True
        except Exception as e:
            print(f"❌ Error while deleting Sample: {e}")
            return False

    # --------------------------
    # Orchestrate full test
    # --------------------------
    def run_test(self, sample_path: str) -> bool:
        print("🚀 Starting SeaweedFS storage leak integration test")
        print("=" * 60)

        # Count files before
        try:
            initial_count = get_seaweed_file_count()
        except Exception as e:
            print("Exception while getting SeaweedFS file count: %s" % e)
            raise e

        print()

        # Upload sample via API
        upload_result = self.upload_file(sample_path)
        if not upload_result:
            return False
        sha1_hash, already_existed = upload_result

        print()

        # Wait for processing to complete (skip if sample already existed — just delete it)
        if not already_existed:
            if not self.wait_for_processing(sha1_hash):
                print("❌ Processing did not complete within timeout")
                return False
            print()
        else:
            print("⏭ Skipping wait (sample already existed); proceeding to delete.\n")

        # Delete sample via Django ORM
        if not self.delete_sample_from_django(sha1_hash):
            print("❌ Failed to delete Sample through Django ORM")
            return False

        # Give SeaweedFS a short moment to process deletions
        time.sleep(5)

        print()

        # Count files after
        try:
            final_count = get_seaweed_file_count()
        except Exception as e:
            print("Exception while getting SeaweedFS file count: %s" % e)
            return False

        print()
        print("=" * 60)
        print(f"📦 SeaweedFS file count before: {initial_count}")
        print(f"📦 SeaweedFS file count after : {final_count}")

        if initial_count == final_count:
            print("🎉 Integration test PASSED!")
            print("✅ No net increase in SeaweedFS file count (no storage leak detected).")
            return True

        print("💥 Integration test FAILED!")
        print("❌ SeaweedFS file count increased, indicating a potential storage leak.")
        return False


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python3 tests/test_seaweed_storage_leak_integration.py /path/to/sample.bin"
        )
        sys.exit(1)

    sample_path = sys.argv[1]

    test = SeaweedStorageLeakIntegrationTest()
    success = test.run_test(sample_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
