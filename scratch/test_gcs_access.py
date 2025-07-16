#!/usr/bin/env python3
"""
Test script to verify GCS access to public test-platform-results bucket.
"""

from google.cloud import storage


def test_anonymous_gcs_access():
    """Test accessing the public GCS bucket anonymously."""
    try:
        print("Testing anonymous GCS access...")

        # Create anonymous client (for public buckets)
        client = storage.Client.create_anonymous_client()
        bucket = client.bucket("test-platform-results")

        # Test data from the prow link
        base_dir = "logs/periodic-ci-redhat-developer-rhdh-main-e2e-tests-gke-operator-nightly/1945046040382017536"
        artifacts_dir = f"{base_dir}/artifacts/"

        print(f"Testing directory listing for: {artifacts_dir}")

        # First, let's see if the base directory exists
        base_blobs = list(bucket.list_blobs(prefix=base_dir, max_results=10))
        print(f"Found {len(base_blobs)} items in base directory:")
        for blob in base_blobs[:5]:
            print(f"  {blob.name}")

        # Test directory listing
        blobs = bucket.list_blobs(prefix=artifacts_dir, delimiter="/")
        directories = []
        files = []

        # Check both directories and files
        for blob in blobs:
            print(f"Found blob: {blob.name}")
            files.append(blob.name)

        for prefix_obj in blobs.prefixes:
            dir_name = prefix_obj.rstrip("/").split("/")[-1]
            directories.append(dir_name)
            print(f"Found directory: {dir_name}")

        print(f"Total directories: {len(directories)}")
        print(f"Total files: {len(files)}")

        e2e_dirs = [d for d in directories if d.startswith("e2e-tests-")]
        print(f"E2E test directories: {e2e_dirs}")

        if e2e_dirs:
            print("✅ Successfully accessed GCS bucket and found e2e test directories!")
            return True
        else:
            print("⚠️  Accessed GCS but no e2e test directories found")
            return False

    except Exception as e:
        print(f"❌ Error accessing GCS: {e}")
        return False


def test_authenticated_gcs_access():
    """Test accessing with default credentials (should fail for public buckets)."""
    try:
        print("\nTesting authenticated GCS access...")

        # Regular client (requires authentication)
        client = storage.Client()
        bucket = client.bucket("test-platform-results")

        base_dir = "logs/periodic-ci-redhat-developer-rhdh-main-e2e-tests-gke-operator-nightly/1945046040382017536"
        artifacts_dir = f"{base_dir}/artifacts/"

        blobs = bucket.list_blobs(prefix=artifacts_dir, delimiter="/")
        directories = []
        for prefix_obj in blobs.prefixes:
            dir_name = prefix_obj.rstrip("/").split("/")[-1]
            directories.append(dir_name)

        print("✅ Authenticated access also works")
        return True

    except Exception as e:
        print(f"❌ Authenticated access failed (expected): {e}")
        return False


if __name__ == "__main__":
    print("Testing GCS access methods for public bucket...")

    # Test anonymous access first
    anonymous_works = test_anonymous_gcs_access()

    # Test authenticated access
    authenticated_works = test_authenticated_gcs_access()

    print("\nResults:")
    print(f"Anonymous access: {'✅ Works' if anonymous_works else '❌ Failed'}")
    print(f"Authenticated access: {'✅ Works' if authenticated_works else '❌ Failed'}")

    if anonymous_works:
        print("\n✅ Use anonymous client for public bucket access")
    else:
        print("\n❌ Need to debug GCS access further")
