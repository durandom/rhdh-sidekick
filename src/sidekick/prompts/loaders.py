"""
Prompt template loaders for various file formats.

This module provides utilities to load prompt templates from files,
supporting YAML, JSON, and plain text formats with variable substitution
and template composition features.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from .base import BasePromptTemplate, PromptConfig


class PromptLoader(ABC):
    """Abstract base class for prompt template loaders."""

    def __init__(self, base_path: Path | None = None):
        """
        Initialize the prompt loader.

        Args:
            base_path: Base directory for resolving relative template paths
        """
        self.base_path = base_path or Path("prompts/templates")

    @abstractmethod
    def load(self, path: Path | str) -> BasePromptTemplate:
        """
        Load a prompt template from a file.

        Args:
            path: Path to the template file

        Returns:
            BasePromptTemplate instance
        """
        pass

    def resolve_path(self, path: Path | str) -> Path:
        """
        Resolve a template path relative to the base path.

        Args:
            path: Path to resolve

        Returns:
            Resolved absolute path
        """
        path = Path(path)
        if not path.is_absolute():
            path = self.base_path / path
        return path


class YAMLPromptLoader(PromptLoader):
    """Loader for YAML-based prompt templates."""

    def load(self, path: Path | str) -> BasePromptTemplate:
        """
        Load a prompt template from a YAML file.

        YAML Structure:
        ```yaml
        name: template_name
        version: "1.0"
        description: Template description
        variables:
          var1: default_value
          var2: another_default
        includes:  # Optional: include other templates
          - shared/common_instructions.yaml
        template: |
          Your prompt template content here with {var1} and {var2}
        ```

        Args:
            path: Path to the YAML file

        Returns:
            BasePromptTemplate instance
        """
        resolved_path = self.resolve_path(path)
        logger.debug(f"Loading YAML prompt template from: {resolved_path}")

        try:
            with open(resolved_path) as f:
                data = yaml.safe_load(f)

            # Extract configuration
            config = PromptConfig(
                name=data.get("name", resolved_path.stem),
                version=data.get("version", "1.0"),
                description=data.get("description", ""),
                variables=data.get("variables", {}),
                metadata=data.get("metadata", {}),
            )

            # Handle includes
            template_content = self._process_includes(data, resolved_path.parent)

            # Add main template content
            if "template" in data:
                template_content = (
                    template_content + "\n\n" + data["template"] if template_content else data["template"]
                )

            return BasePromptTemplate(
                config=config,
                template_content=template_content,
                template_path=resolved_path,
            )

        except Exception as e:
            logger.error(f"Failed to load YAML prompt template from {resolved_path}: {e}")
            raise

    def _process_includes(self, data: dict[str, Any], base_dir: Path) -> str:
        """
        Process included templates.

        Args:
            data: YAML data dictionary
            base_dir: Base directory for resolving includes

        Returns:
            Combined template content from includes
        """
        includes = data.get("includes", [])
        if not includes:
            return ""

        included_content = []
        for include_path in includes:
            # Try to resolve relative to the template's directory first
            include_resolved = base_dir / include_path

            # If that doesn't exist, try relative to the base templates directory
            if not include_resolved.exists():
                include_resolved = self.base_path / include_path

            logger.debug(f"Including template from: {include_resolved}")
            included_template = self.load(include_resolved)
            included_content.append(included_template.template_content)

        return "\n\n".join(included_content)


class JSONPromptLoader(PromptLoader):
    """Loader for JSON-based prompt templates."""

    def load(self, path: Path | str) -> BasePromptTemplate:
        """
        Load a prompt template from a JSON file.

        Args:
            path: Path to the JSON file

        Returns:
            BasePromptTemplate instance
        """
        resolved_path = self.resolve_path(path)
        logger.debug(f"Loading JSON prompt template from: {resolved_path}")

        try:
            with open(resolved_path) as f:
                data = json.load(f)

            config = PromptConfig(
                name=data.get("name", resolved_path.stem),
                version=data.get("version", "1.0"),
                description=data.get("description", ""),
                variables=data.get("variables", {}),
                metadata=data.get("metadata", {}),
            )

            template_content = data.get("template", "")

            return BasePromptTemplate(
                config=config,
                template_content=template_content,
                template_path=resolved_path,
            )

        except Exception as e:
            logger.error(f"Failed to load JSON prompt template from {resolved_path}: {e}")
            raise


class TextPromptLoader(PromptLoader):
    """Loader for plain text prompt templates."""

    def load(self, path: Path | str, name: str | None = None) -> BasePromptTemplate:
        """
        Load a prompt template from a plain text file.

        Args:
            path: Path to the text file
            name: Optional name for the template

        Returns:
            BasePromptTemplate instance
        """
        resolved_path = self.resolve_path(path)
        logger.debug(f"Loading text prompt template from: {resolved_path}")

        try:
            template_content = resolved_path.read_text()

            config = PromptConfig(
                name=name or resolved_path.stem,
                description=f"Loaded from {resolved_path.name}",
            )

            return BasePromptTemplate(
                config=config,
                template_content=template_content,
                template_path=resolved_path,
            )

        except Exception as e:
            logger.error(f"Failed to load text prompt template from {resolved_path}: {e}")
            raise


def get_loader(file_path: Path | str) -> PromptLoader:
    """
    Get the appropriate loader based on file extension.

    Args:
        file_path: Path to the template file

    Returns:
        Appropriate PromptLoader instance
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension in [".yaml", ".yml"]:
        return YAMLPromptLoader()
    elif extension == ".json":
        return JSONPromptLoader()
    else:
        return TextPromptLoader()


def load_prompt_template(
    path: Path | str,
    base_path: Path | None = None,
    loader: PromptLoader | None = None,
) -> BasePromptTemplate:
    """
    Convenience function to load a prompt template from a file.

    Args:
        path: Path to the template file
        base_path: Base directory for resolving relative paths
        loader: Optional specific loader to use

    Returns:
        BasePromptTemplate instance
    """
    if loader is None:
        loader = get_loader(path)

    if base_path:
        loader.base_path = base_path

    return loader.load(path)
