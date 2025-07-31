"""
Workspace management mixin for agents.

Provides common functionality for workspace directory setup and file operations.
"""

from pathlib import Path

from agno.tools.file import FileTools
from loguru import logger


class WorkspaceMixin:
    """Mixin for workspace and file operations management."""

    def __init__(self, *args, workspace_dir: Path | None = None, **kwargs):
        """Initialize workspace mixin.

        Args:
            workspace_dir: Path to workspace directory for file operations
            *args: Passed to super().__init__()
            **kwargs: Passed to super().__init__()
        """
        super().__init__(*args, **kwargs)
        self.workspace_dir = workspace_dir or Path("./workspace")
        logger.debug(f"WorkspaceMixin initialized: workspace_dir={self.workspace_dir}")

    def create_file_tools(self) -> FileTools:
        """Create and return configured FileTools for workspace operations.

        Returns:
            Configured FileTools instance
        """
        logger.debug(f"Creating FileTools with base_dir={self.workspace_dir}")
        return FileTools(base_dir=self.workspace_dir)
