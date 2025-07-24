"""
Prompt template registry for managing and accessing templates.

This module provides a centralized registry for prompt templates,
allowing agents to easily access and manage their prompts.
"""

from pathlib import Path

from loguru import logger

from .base import BasePromptTemplate
from .loaders import load_prompt_template


class PromptRegistry:
    """Registry for managing prompt templates."""

    def __init__(self, base_path: Path | None = None):
        """
        Initialize the prompt registry.

        Args:
            base_path: Base directory for template files
        """
        self.base_path = base_path or Path(__file__).parent / "templates"
        self._templates: dict[str, BasePromptTemplate] = {}
        self._template_paths: dict[str, Path] = {}

    def register(self, name: str, template: BasePromptTemplate | Path | str) -> None:
        """
        Register a prompt template.

        Args:
            name: Name to register the template under
            template: BasePromptTemplate instance or path to template file
        """
        if isinstance(template, Path | str):
            # Load template from file
            template_path = Path(template)
            if not template_path.is_absolute():
                template_path = self.base_path / template_path

            self._template_paths[name] = template_path
            # Lazy loading - don't load until needed
            logger.debug(f"Registered template path '{name}' -> {template_path}")
        else:
            self._templates[name] = template
            logger.debug(f"Registered template instance '{name}'")

    def get(self, name: str, reload: bool = False) -> BasePromptTemplate:
        """
        Get a registered prompt template.

        Args:
            name: Name of the template
            reload: Force reload from file if applicable

        Returns:
            BasePromptTemplate instance

        Raises:
            KeyError: If template not found
        """
        # Check if we need to load from file
        if name in self._template_paths and (reload or name not in self._templates):
            logger.debug(f"Loading template '{name}' from file")
            self._templates[name] = load_prompt_template(
                self._template_paths[name],
                base_path=self.base_path,
            )

        if name not in self._templates:
            raise KeyError(f"Template '{name}' not found in registry")

        return self._templates[name]

    def list_templates(self) -> list[str]:
        """
        List all registered template names.

        Returns:
            List of template names
        """
        # Combine both in-memory and file-based templates
        all_names = set(self._templates.keys()) | set(self._template_paths.keys())
        return sorted(all_names)

    def auto_discover(self, directory: Path | None = None) -> None:
        """
        Auto-discover and register templates from a directory.

        Args:
            directory: Directory to scan (defaults to base_path)
        """
        scan_dir = directory or self.base_path
        logger.info(f"Auto-discovering templates in: {scan_dir}")

        if not scan_dir.exists():
            logger.warning(f"Template directory does not exist: {scan_dir}")
            return

        # Find all YAML/JSON files
        for pattern in ["**/*.yaml", "**/*.yml", "**/*.json"]:
            for template_file in scan_dir.glob(pattern):
                # Create a name from the relative path
                relative_path = template_file.relative_to(scan_dir)
                name = str(relative_path.with_suffix("")).replace("/", ".")

                self.register(name, template_file)
                logger.debug(f"Auto-discovered template: {name}")

    def clear(self) -> None:
        """Clear all registered templates."""
        self._templates.clear()
        self._template_paths.clear()
        logger.debug("Cleared prompt registry")


# Global registry instance
_global_registry: PromptRegistry | None = None


def get_prompt_registry(base_path: Path | None = None) -> PromptRegistry:
    """
    Get the global prompt registry instance.

    Args:
        base_path: Base directory for template files

    Returns:
        Global PromptRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        # Use the default templates directory if no base_path provided
        if base_path is None:
            base_path = Path(__file__).parent / "templates"
        _global_registry = PromptRegistry(base_path)
        # Auto-discover templates on first access
        _global_registry.auto_discover()
    return _global_registry


def register_prompt(name: str, template: BasePromptTemplate | Path | str) -> None:
    """
    Register a prompt template in the global registry.

    Args:
        name: Name to register the template under
        template: BasePromptTemplate instance or path to template file
    """
    registry = get_prompt_registry()
    registry.register(name, template)


def get_prompt(name: str, reload: bool = False) -> BasePromptTemplate:
    """
    Get a prompt template from the global registry.

    Args:
        name: Name of the template
        reload: Force reload from file if applicable

    Returns:
        BasePromptTemplate instance
    """
    registry = get_prompt_registry()
    return registry.get(name, reload=reload)
