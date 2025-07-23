"""Base classes for knowledge sources."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .config import GDriveSourceConfig, GitSourceConfig, WebSourceConfig


class KnowledgeSourceConfig(BaseModel):
    """Base configuration for knowledge sources."""

    type: str
    name: str = Field(..., description="Source name, becomes the directory name")


class DownloadResult(BaseModel):
    """Result of a download operation."""

    source_name: str
    files_downloaded: list[Path] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    success: bool = True


class KnowledgeSource(ABC):
    """Abstract base class for knowledge sources."""

    def __init__(self, config: "GDriveSourceConfig | GitSourceConfig | WebSourceConfig", base_path: Path | None = None):
        """Initialize knowledge source.

        Args:
            config: Source configuration
            base_path: Base path for knowledge storage (default: knowledge/)
        """
        self.config: GDriveSourceConfig | GitSourceConfig | WebSourceConfig = config
        self.base_path = base_path or Path("knowledge")
        self.output_dir = self.base_path / config.name

    @abstractmethod
    def download(self, **kwargs) -> DownloadResult:
        """Download content from the source.

        Returns:
            DownloadResult with list of downloaded files
        """
        pass

    @abstractmethod
    def sync(self, manifest: dict[str, Any] | None = None) -> DownloadResult:
        """Sync content based on configuration.

        Args:
            manifest: Previous manifest for tracking changes

        Returns:
            DownloadResult with list of downloaded files
        """
        pass

    def ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
