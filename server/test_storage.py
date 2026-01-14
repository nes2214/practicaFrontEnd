# test_storage.py
# -----------------------------
# Tests for Filebase/MinIO storage client
# -----------------------------
# This module tests the MinIO client connection and ensures that
# the expected bucket exists.
# -----------------------------

from storage import client


def test_list():
    """
    Verify that the storage client can list buckets and that the
    expected bucket ('dawbio2-test') exists.
    """
    buckets = client.list_buckets()
    bucket_names = [bucket.name for bucket in buckets]
    assert "dawbio2-test" in bucket_names, f"Bucket 'dawbio2-test' not found. Available buckets: {bucket_names}"