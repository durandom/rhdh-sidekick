"""Configuration handling for knowledge sources."""

from pathlib import Path
from typing import Any, Literal

import yaml
from loguru import logger
from pydantic import BaseModel, Field, field_validator


class GDriveSourceConfig(BaseModel):
    """Configuration for Google Drive source."""

    type: Literal["gdrive"] = "gdrive"
    name: str
    documents: list[dict[str, Any]] = Field(default_factory=list)
    export_format: str = "md"

    @field_validator("documents", mode="before")
    @classmethod
    def validate_documents(cls, v):
        """Validate document entries."""
        if not isinstance(v, list):
            raise ValueError("documents must be a list")

        for doc in v:
            if not isinstance(doc, dict) or "url" not in doc:
                raise ValueError("Each document must have a 'url' field")
        return v


class GitSourceConfig(BaseModel):
    """Configuration for Git repository source."""

    type: Literal["git"] = "git"
    name: str
    url: str
    branch: str = "main"
    files: list[str] = Field(default_factory=list)
    follow_links: bool = True


class WebSourceConfig(BaseModel):
    """Configuration for web source."""

    type: Literal["web"] = "web"
    name: str
    urls: list[str] = Field(default_factory=list)
    depth: int = Field(default=1, ge=0, le=5)
    patterns: list[str] = Field(default_factory=list)
    export_format: str = "md"


class KnowledgeConfig(BaseModel):
    """Main configuration for knowledge sources."""

    sources: list[GDriveSourceConfig | GitSourceConfig | WebSourceConfig] = Field(default_factory=list)

    @classmethod
    def load_from_file(cls, config_path: Path) -> "KnowledgeConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            KnowledgeConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or "sources" not in data:
                raise ValueError("Configuration must contain 'sources' key")

            # Parse sources with proper type discrimination
            sources: list[GDriveSourceConfig | GitSourceConfig | WebSourceConfig] = []
            for source_data in data["sources"]:
                source_type = source_data.get("type")
                if source_type == "gdrive":
                    sources.append(GDriveSourceConfig(**source_data))
                elif source_type == "git":
                    sources.append(GitSourceConfig(**source_data))
                elif source_type == "web":
                    sources.append(WebSourceConfig(**source_data))
                else:
                    raise ValueError(f"Unknown source type: {source_type}")

            config = cls(sources=sources)
            logger.info(f"Loaded {len(config.sources)} sources from {config_path}")
            return config

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}") from e
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file.

        Args:
            config_path: Path to save configuration
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {"sources": [source.model_dump() for source in self.sources]}

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Saved configuration to {config_path}")

    def get_source_by_name(self, name: str) -> GDriveSourceConfig | GitSourceConfig | WebSourceConfig | None:
        """Get source configuration by name.

        Args:
            name: Source name

        Returns:
            Source configuration or None if not found
        """
        for source in self.sources:
            if source.name == name:
                return source
        return None
