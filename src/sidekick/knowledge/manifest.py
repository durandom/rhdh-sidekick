"""Manifest handling for tracking downloaded files."""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field


class Manifest(BaseModel):
    """Manifest for tracking downloaded files."""

    source: str
    last_sync: datetime = Field(default_factory=datetime.now)
    files: list[str] = Field(default_factory=list)

    def save(self, manifest_dir: Path) -> None:
        """Save manifest to JSON file.

        Args:
            manifest_dir: Directory to save manifest files
        """
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = manifest_dir / f"{self.source}.json"

        data = self.model_dump(mode="json")
        data["last_sync"] = self.last_sync.isoformat()

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Saved manifest for {self.source} with {len(self.files)} files")

    @classmethod
    def load(cls, source: str, manifest_dir: Path) -> "Manifest | None":
        """Load manifest from JSON file.

        Args:
            source: Source name
            manifest_dir: Directory containing manifest files

        Returns:
            Manifest instance or None if not found
        """
        manifest_file = manifest_dir / f"{source}.json"

        if not manifest_file.exists():
            logger.debug(f"No manifest found for {source}")
            return None

        try:
            with open(manifest_file, encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        except Exception as e:
            logger.error(f"Failed to load manifest for {source}: {e}")
            return None

    def cleanup_removed_files(self, current_files: list[Path], base_path: Path) -> list[Path]:
        """Remove files that were in manifest but not in current download.

        Args:
            current_files: List of files from current download
            base_path: Base path for resolving relative paths

        Returns:
            List of removed files
        """
        current_file_strs = {str(f.relative_to(base_path)) for f in current_files}
        removed_files = []

        for file_str in self.files:
            if file_str not in current_file_strs:
                file_path = base_path / file_str
                if file_path.exists():
                    try:
                        file_path.unlink()
                        removed_files.append(file_path)
                        logger.debug(f"Removed old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove {file_path}: {e}")

        # Clean up empty directories
        for file_path in removed_files:
            parent = file_path.parent
            while parent != base_path and parent.exists():
                try:
                    if not any(parent.iterdir()):
                        parent.rmdir()
                        logger.debug(f"Removed empty directory: {parent}")
                    parent = parent.parent
                except Exception:
                    break

        return removed_files


class ManifestManager:
    """Manages manifests for all knowledge sources."""

    def __init__(self, base_path: Path | None = None):
        """Initialize manifest manager.

        Args:
            base_path: Base path for knowledge storage
        """
        self.base_path = base_path or Path("knowledge")
        self.manifest_dir = self.base_path / ".manifests"

    def get_manifest(self, source: str) -> Manifest | None:
        """Get manifest for a source."""
        return Manifest.load(source, self.manifest_dir)

    def save_manifest(self, source: str, files: list[Path]) -> None:
        """Save manifest for a source.

        Args:
            source: Source name
            files: List of downloaded files
        """
        manifest = Manifest(
            source=source,
            files=[str(f.relative_to(self.base_path)) for f in files],
        )
        manifest.save(self.manifest_dir)

    def sync_and_cleanup(self, source: str, current_files: list[Path]) -> list[Path]:
        """Sync manifest and cleanup removed files.

        Args:
            source: Source name
            current_files: List of files from current download

        Returns:
            List of removed files
        """
        removed_files = []
        manifest = self.get_manifest(source)

        if manifest:
            removed_files = manifest.cleanup_removed_files(current_files, self.base_path)

        self.save_manifest(source, current_files)
        return removed_files
