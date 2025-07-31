"""
Storage management mixin for agents.

Provides common functionality for SQLite storage creation with custom table naming.
"""

from pathlib import Path

from agno.storage.sqlite import SqliteStorage
from loguru import logger


class StorageMixin:
    """Mixin for storage creation and management."""

    def __init__(self, *args, storage_path: Path | None = None, **kwargs):
        """Initialize storage mixin.

        Args:
            storage_path: Path for agent session storage
            *args: Passed to super().__init__()
            **kwargs: Passed to super().__init__()
        """
        super().__init__(*args, **kwargs)
        self.storage_path = storage_path
        logger.debug(f"StorageMixin initialized: storage_path={storage_path}")

    def create_storage(self, table_name: str) -> SqliteStorage:
        """Create and return configured storage for the agent.

        Args:
            table_name: Name of the database table to use

        Returns:
            Configured SqliteStorage instance
        """
        # Create storage directory if needed
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        storage = SqliteStorage(
            table_name=table_name,
            db_file=str(self.storage_path),
        )

        logger.debug(f"Created agent storage at {self.storage_path} with table {table_name}")
        return storage
