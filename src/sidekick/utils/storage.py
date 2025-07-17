"""
Google Cloud Storage utilities for the sidekick application.

This module provides utilities for interacting with Google Cloud Storage,
including file operations and bucket management.
"""

from pathlib import Path

from google.cloud import storage
from loguru import logger


class GCSStorageClient:
    """Google Cloud Storage client for test artifact access."""

    def __init__(self, bucket_name: str = "test-platform-results"):
        """Initialize GCS client with bucket name."""
        self.bucket_name = bucket_name
        self._client = None
        self._bucket = None
        logger.debug(f"GCS client configured for bucket: {bucket_name}")

    @property
    def client(self):
        """Lazy initialize GCS client."""
        if self._client is None:
            # Use anonymous client for public buckets
            self._client = storage.Client.create_anonymous_client()
            logger.debug("Initialized anonymous GCS client for public bucket")
        return self._client

    @property
    def bucket(self):
        """Lazy initialize GCS bucket."""
        if self._bucket is None:
            self._bucket = self.client.bucket(self.bucket_name)
            logger.debug(f"Initialized GCS bucket: {self.bucket_name}")
        return self._bucket

    def get_text_from_blob(self, blob_path: str) -> str:
        """Get text content from a blob."""
        try:
            blob = self.bucket.blob(blob_path)
            content = blob.download_as_text()
            logger.debug(f"Retrieved text from blob: {blob_path} ({len(content)} chars)")
            return str(content)
        except Exception as e:
            logger.error(f"Error reading blob {blob_path}: {e}")
            raise

    def get_bytes_from_blob(self, blob_path: str) -> bytes:
        """Get bytes content from a blob."""
        try:
            blob = self.bucket.blob(blob_path)
            content = blob.download_as_bytes()
            logger.debug(f"Retrieved bytes from blob: {blob_path} ({len(content)} bytes)")
            return bytes(content)
        except Exception as e:
            logger.error(f"Error reading blob {blob_path}: {e}")
            raise

    def blob_exists(self, blob_path: str) -> bool:
        """Check if a blob exists."""
        try:
            blob = self.bucket.blob(blob_path)
            exists = blob.exists()
            logger.debug(f"Blob exists check for {blob_path}: {exists}")
            return bool(exists)
        except Exception as e:
            logger.debug(f"Error checking blob existence {blob_path}: {e}")
            return False

    def list_blobs(self, prefix: str) -> list[str]:
        """List all blobs with given prefix."""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            blob_names = [blob.name for blob in blobs]
            logger.debug(f"Listed {len(blob_names)} blobs with prefix: {prefix}")
            return blob_names
        except Exception as e:
            logger.error(f"Error listing blobs with prefix {prefix}: {e}")
            raise

    def get_immediate_files(self, prefix: str) -> list[str]:
        """Get immediate files (not directories) from prefix."""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix, delimiter="/")
            # Get just the filenames, not full paths
            files = []
            for blob in blobs:
                if blob.name != prefix and not blob.name.endswith("/"):
                    # Extract just the filename from the full path
                    filename = blob.name.split("/")[-1]
                    files.append(filename)
            logger.debug(f"Found {len(files)} immediate files in {prefix}")
            return files
        except Exception as e:
            logger.error(f"Error getting immediate files from {prefix}: {e}")
            raise

    def get_immediate_directories(self, prefix: str) -> list[str]:
        """Get immediate directories from prefix."""
        try:
            dirs = set()
            for blob in self.bucket.list_blobs(prefix=prefix):
                # Get the part after the prefix
                relative_path = blob.name[len(prefix) :]
                # Only get the first directory name (before any slash)
                if relative_path and "/" in relative_path:
                    dir_name = relative_path.split("/")[0]
                    dirs.add(dir_name)

            directories = sorted(list(dirs))
            logger.debug(f"Found {len(directories)} immediate directories in {prefix}: {directories}")
            return directories
        except Exception as e:
            logger.error(f"Error getting immediate directories from {prefix}: {e}")
            # Return empty list instead of raising to allow graceful degradation
            return []

    def download_to_file(self, blob_path: str, local_path: Path) -> bool:
        """Download a blob to a local file with debugging output."""
        try:
            blob = self.bucket.blob(blob_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            blob.download_to_filename(str(local_path))

            file_size = local_path.stat().st_size
            logger.info(f"Downloaded {blob_path} -> {local_path} ({file_size} bytes)")
            return True
        except Exception as e:
            logger.error(f"Failed to download {blob_path} to {local_path}: {e}")
            return False


# Global storage client instance
storage_client = GCSStorageClient()
