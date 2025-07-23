"""Git repository knowledge source implementation."""

import hashlib
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from loguru import logger

from .base import DownloadResult, KnowledgeSource
from .config import GitSourceConfig


class GitSource(KnowledgeSource):
    """Git repository knowledge source."""

    def __init__(self, config: GitSourceConfig, base_path: Path | None = None):
        """Initialize Git source.

        Args:
            config: Git source configuration
            base_path: Base path for knowledge storage
        """
        super().__init__(config, base_path)
        self.config: GitSourceConfig = config

    def download(self, **kwargs) -> DownloadResult:
        """Download files from git repository.

        Keyword Args:
            url: Repository URL
            branch: Branch to checkout
            files: File patterns to copy

        Returns:
            DownloadResult with downloaded files
        """
        url = kwargs.get("url", self.config.url)
        branch = kwargs.get("branch", self.config.branch)
        files = kwargs.get("files", self.config.files)

        return self._clone_and_copy(url, branch, files)

    def sync(self, manifest: dict[str, Any] | None = None) -> DownloadResult:
        """Sync git repository based on configuration.

        Args:
            manifest: Previous manifest (not used for Git)

        Returns:
            DownloadResult with downloaded files
        """
        return self._clone_and_copy(self.config.url, self.config.branch, self.config.files)

    def _get_repo_cache_path(self, url: str, branch: str) -> Path:
        """Generate a unique cache path for a repository based on URL and branch.

        Args:
            url: Repository URL
            branch: Branch name

        Returns:
            Path to the cache directory for this repo/branch combination
        """
        # Parse URL to get a clean repository identifier
        parsed = urlparse(url)
        repo_name = parsed.path.strip("/").replace("/", "_").replace(".git", "")

        # Create a hash of URL + branch for uniqueness
        content = f"{url}#{branch}"
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]

        # Create cache directory path
        cache_dir = Path.cwd() / "tmp" / f"{repo_name}_{branch}_{hash_suffix}"
        return cache_dir

    def _clone_and_copy(self, url: str, branch: str, file_patterns: list[str]) -> DownloadResult:
        """Clone repository and copy specified files.

        Args:
            url: Repository URL
            branch: Branch to checkout
            file_patterns: File patterns to copy (glob patterns)

        Returns:
            DownloadResult with downloaded files
        """
        result = DownloadResult(source_name=self.config.name)

        # Ensure output directory exists
        self.ensure_output_dir()

        # Get persistent cache path
        repo_path = self._get_repo_cache_path(url, branch)

        try:
            # Ensure tmp directory exists
            repo_path.parent.mkdir(parents=True, exist_ok=True)

            if repo_path.exists():
                # Repository already exists, pull latest changes
                logger.info(f"Repository cache exists at {repo_path}, pulling latest changes")
                try:
                    # Navigate to repo and pull
                    pull_cmd = ["git", "-C", str(repo_path), "pull", "origin", branch]
                    subprocess.run(
                        pull_cmd,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    logger.debug(f"Successfully pulled latest changes for {url}")
                except subprocess.CalledProcessError as e:
                    logger.warning(
                        f"Git pull failed, will proceed with existing repository: {e.stderr if e.stderr else str(e)}"
                    )
            else:
                # Clone repository with shallow clone
                logger.info(f"Cloning {url} (branch: {branch}) to {repo_path}")
                clone_cmd = [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    branch,
                    url,
                    str(repo_path),
                ]

                subprocess.run(
                    clone_cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                logger.debug(f"Successfully cloned to {repo_path}")

            # Copy files based on patterns
            copied_files = []
            for pattern in file_patterns:
                files = list(repo_path.glob(pattern))
                logger.debug(f"Pattern '{pattern}' matched {len(files)} files")

                for src_file in files:
                    if src_file.is_file():
                        # Calculate relative path from repo root
                        rel_path = src_file.relative_to(repo_path)
                        dest_file = self.output_dir / rel_path

                        # Create destination directory
                        dest_file.parent.mkdir(parents=True, exist_ok=True)

                        # Handle symlinks based on configuration
                        if src_file.is_symlink():
                            if self.config.follow_links:
                                # Follow symlink and copy actual file
                                try:
                                    target = src_file.resolve()
                                    if target.exists() and target.is_file():
                                        shutil.copy2(target, dest_file)
                                        copied_files.append(dest_file)
                                        logger.debug(f"Copied symlink target: {rel_path}")
                                    else:
                                        logger.warning(f"Symlink points to non-existent file: {rel_path}")
                                except Exception as e:
                                    logger.warning(f"Failed to resolve symlink {rel_path}: {e}")
                            else:
                                # Skip symlinks
                                logger.debug(f"Skipping symlink: {rel_path}")
                                continue
                        else:
                            # Regular file
                            try:
                                shutil.copy2(src_file, dest_file)
                                copied_files.append(dest_file)
                                logger.debug(f"Copied: {rel_path}")
                            except Exception as e:
                                error_msg = f"Failed to copy {rel_path}: {e}"
                                logger.error(error_msg)
                                result.errors.append(error_msg)

            result.files_downloaded = copied_files
            logger.info(f"Copied {len(copied_files)} files from {url}")

        except subprocess.CalledProcessError as e:
            error_msg = f"Git operation failed: {e.stderr if e.stderr else str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            result.success = False

        except Exception as e:
            error_msg = f"Failed to process git repository: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
            result.success = False

        # Set success based on whether we copied any files
        if result.success:
            result.success = len(result.files_downloaded) > 0

        return result

    @staticmethod
    def is_git_available() -> bool:
        """Check if git is available in PATH.

        Returns:
            True if git is available, False otherwise
        """
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
