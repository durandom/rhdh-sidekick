"""
Test analysis utilities for downloading and processing test artifacts.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from loguru import logger

from .storage import storage_client


class TestArtifactDownloader:
    """Downloads test artifacts by mirroring GCS directory structure."""

    def __init__(self, prow_link: str, base_output_dir: str = "downloads"):
        """
        Initialize the test artifact downloader.

        Args:
            prow_link: Full Prow CI link (e.g., "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456")
            base_output_dir: Base output directory (default: "downloads")
        """
        self.prow_link = prow_link
        self.base_output_dir = base_output_dir

        # Extract base directory from prow link
        self.base_dir = self._extract_base_dir(prow_link)

        # Create sanitized work directory
        sanitized_subdir = self._sanitize_url_to_path(prow_link)
        self.work_dir = Path(base_output_dir) / sanitized_subdir

        self.downloaded_files: dict[str, Path] = {}
        self.failed_downloads: list[str] = []

        logger.info(
            f"TestArtifactDownloader initialized: prow_link={prow_link}, "
            f"base_dir={self.base_dir}, work_dir={self.work_dir}"
        )

    @classmethod
    def with_work_dir(cls, prow_link: str, work_dir: Path) -> "TestArtifactDownloader":
        """Create a downloader with a specific work directory (for cached artifacts)."""
        downloader = cls.__new__(cls)
        downloader.prow_link = prow_link
        downloader.base_output_dir = str(work_dir.parent)
        downloader.base_dir = downloader._extract_base_dir(prow_link)
        downloader.work_dir = work_dir
        downloader.downloaded_files = {}
        downloader.failed_downloads = []

        logger.info(
            f"TestArtifactDownloader initialized with work_dir: prow_link={prow_link}, "
            f"base_dir={downloader.base_dir}, work_dir={work_dir}"
        )
        return downloader

    def _extract_base_dir(self, prow_link: str) -> str:
        """Extract base directory from prow link."""
        import re

        pattern = r"https://prow\.ci\.openshift\.org/view/gs/test-platform-results/(logs/[^|>\s/]+(?:/[^|>\s/]+)*)"
        match = re.search(pattern, prow_link)

        if not match:
            raise ValueError(
                f"Invalid prow link format: {prow_link}. Expected format: https://prow.ci.openshift.org/view/gs/test-platform-results/logs/..."
            )

        return match.group(1)

    def _sanitize_url_to_path(self, url: str) -> str:
        """Convert a URL to a sanitized directory path."""
        import re

        # Remove protocol and domain
        if "://prow.ci.openshift.org/view/gs/test-platform-results/" in url:
            path_part = url.split("://prow.ci.openshift.org/view/gs/test-platform-results/")[1]
        else:
            path_part = url

        # Replace problematic characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", path_part)

        # Replace multiple underscores with single underscore
        sanitized = re.sub(r"_+", "_", sanitized)

        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")

        return sanitized

    def download_all_artifacts(self) -> dict[str, dict[str, Path] | list[str]]:
        """Download all artifacts by mirroring the base_dir structure."""
        logger.info("Starting download of all test artifacts")

        # Create the work directory
        self.work_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created work directory: {self.work_dir}")

        try:
            # Get all blobs with this prefix
            blob_names = storage_client.list_blobs(self.base_dir)

            for blob_name in blob_names:
                # Skip if it's just a directory (ends with /)
                if blob_name.endswith("/"):
                    continue

                # Mirror the directory structure
                relative_path = blob_name[len(self.base_dir) :].lstrip("/")
                local_path = self.work_dir / relative_path

                # Check if file already exists
                if local_path.exists() and local_path.stat().st_size > 0:
                    logger.info(f"File already exists, using cached: {blob_name} -> {local_path}")
                    self.downloaded_files[blob_name] = local_path
                    continue

                # Download the file
                if storage_client.download_to_file(blob_name, local_path):
                    self.downloaded_files[blob_name] = local_path
                    logger.info(f"Downloaded: {blob_name} -> {local_path}")
                else:
                    self.failed_downloads.append(blob_name)
                    logger.warning(f"Failed to download: {blob_name}")

        except Exception as e:
            logger.error(f"Error downloading directory {self.base_dir}: {e}")

        logger.info(
            f"Download complete: {len(self.downloaded_files)} files downloaded, {len(self.failed_downloads)} failed"
        )

        # Categorize downloaded files
        junit_files = {}
        build_logs = {}
        pod_logs = {}
        screenshots = {}
        other_files = {}

        for gcs_path, local_path in self.downloaded_files.items():
            relative_path = gcs_path[len(self.base_dir) :].lstrip("/")
            filename = local_path.name.lower()
            if filename.endswith(".xml") and "junit" in filename:
                junit_files[relative_path] = local_path
            elif filename.endswith(".log") and "build" in filename:
                build_logs[relative_path] = local_path
            elif filename.endswith(".log") and "pod" in filename:
                pod_logs[relative_path] = local_path
            elif filename.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                screenshots[relative_path] = local_path
            else:
                other_files[relative_path] = local_path

        return {
            "junit_files": junit_files,
            "build_logs": build_logs,
            "pod_logs": pod_logs,
            "screenshots": screenshots,
            "other_files": other_files,
            "failed_downloads": self.failed_downloads,
        }

    def cleanup(self):
        """Clean up downloaded files."""
        import shutil

        try:
            if self.work_dir.exists():
                shutil.rmtree(self.work_dir)
                logger.info(f"Cleaned up work directory: {self.work_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup work directory {self.work_dir}: {e}")


def extract_failed_testsuites(junit_path: Path) -> str:
    """Extract failed test suites from JUnit XML file."""
    try:
        with open(junit_path) as f:
            xml_content = f.read()

        # Check if the file has been sanitized
        if "potentially sensitive information and has been removed" in xml_content:
            logger.warning(f"JUnit XML file {junit_path} has been sanitized")
            return f"JUnit XML file has been sanitized: {xml_content.strip()}"

        if not xml_content.strip().startswith("<"):
            logger.warning(f"JUnit XML file {junit_path} does not appear to be XML")
            return f"JUnit XML file does not appear to be XML. Content: {xml_content.strip()[:200]}..."

        root = ET.fromstring(xml_content)
        testsuites = [root] if root.tag == "testsuite" else root.findall("testsuite")

        failed_testsuites = []
        for testsuite in testsuites:
            failures = int(testsuite.get("failures", "0"))
            errors = int(testsuite.get("errors", "0"))

            if failures > 0 or errors > 0:
                # Remove system-out elements to reduce noise
                for element in testsuite.iter():
                    system_outs = element.findall("system-out")
                    for system_out in system_outs:
                        element.remove(system_out)

                failed_testsuites.append(ET.tostring(testsuite, encoding="unicode"))

        result = "\n".join(failed_testsuites)
        logger.debug(f"Found {len(failed_testsuites)} failed testsuites in {junit_path}")
        return result

    except Exception as e:
        error_msg = f"Error extracting failed testsuites from {junit_path}: {e}"
        logger.error(error_msg)
        return error_msg


def get_folder_structure(prefix: str) -> str:
    """Get the tree/folder structure output from a GCS prefix."""
    try:
        logger.debug(f"Getting folder structure for: {prefix}")

        blob_names = storage_client.list_blobs(prefix)
        rel_paths = []

        for path in blob_names:
            rel_path = path[len(prefix) :].strip("/")
            if rel_path:
                rel_paths.append(rel_path)

        rel_paths.sort()

        seen_dirs = set()
        tree_output = []

        for path in rel_paths:
            parts = path.split("/")
            for level, part in enumerate(parts):
                current_path = "/".join(parts[: level + 1])
                if current_path not in seen_dirs:
                    seen_dirs.add(current_path)
                    indent = "  " * level
                    if level == len(parts) - 1:
                        tree_output.append(f"{indent}{part}")
                    else:
                        tree_output.append(f"{indent}{part}/")

        result = "\n".join(tree_output)
        logger.debug(f"Generated tree structure with {len(tree_output)} items")
        return result

    except Exception as e:
        error_msg = f"Error getting folder structure for {prefix}: {e}"
        logger.error(error_msg)
        return error_msg
