"""
Knowledge base management mixin for agents.

Provides common functionality for knowledge base loading, KnowledgeTools creation,
and knowledge-related operations.
"""

from pathlib import Path
from typing import Any

from agno.tools.knowledge import KnowledgeTools
from loguru import logger

from ...knowledge import KnowledgeManager


class KnowledgeMixin:
    """Mixin for knowledge base management functionality."""

    def __init__(self, *args, knowledge_path: Path | None = None, **kwargs):
        """Initialize knowledge mixin.

        Args:
            knowledge_path: Path to knowledge documents directory
            *args: Passed to super().__init__()
            **kwargs: Passed to super().__init__()
        """
        super().__init__(*args, **kwargs)
        self.knowledge_manager = KnowledgeManager(knowledge_path=knowledge_path)
        self._knowledge: Any = None  # Will be loaded during setup
        logger.debug(f"KnowledgeMixin initialized: knowledge_path={knowledge_path}")

    async def load_knowledge(self, recreate: bool = False) -> Any:
        """Load knowledge base asynchronously.

        Args:
            recreate: Whether to recreate the knowledge base

        Returns:
            Loaded knowledge base instance
        """
        logger.info("Loading knowledge base")
        self._knowledge = await self.knowledge_manager.aload_knowledge(recreate=recreate)
        return self._knowledge

    def load_knowledge_sync(self, recreate: bool = False) -> Any:
        """Load knowledge base synchronously.

        Args:
            recreate: Whether to recreate the knowledge base

        Returns:
            Loaded knowledge base instance
        """
        logger.info("Loading knowledge base (sync)")
        self._knowledge = self.knowledge_manager.load_knowledge(recreate=recreate)
        return self._knowledge

    def create_knowledge_tools(self, knowledge: Any | None = None) -> KnowledgeTools:
        """Create and return configured KnowledgeTools.

        Args:
            knowledge: Knowledge base instance to use (uses self._knowledge if None)

        Returns:
            Configured KnowledgeTools instance

        Raises:
            RuntimeError: If knowledge base is not loaded
        """
        knowledge_to_use = knowledge or self._knowledge
        if knowledge_to_use is None:
            raise RuntimeError("Knowledge base not loaded. Call load_knowledge() first.")

        return KnowledgeTools(
            knowledge=knowledge_to_use,
            think=True,
            search=True,
            analyze=True,
            add_instructions=True,
            add_few_shot=True,
        )

    @property
    def knowledge(self) -> Any:
        """Get the loaded knowledge base.

        Returns:
            Loaded knowledge base instance or None if not loaded
        """
        return self._knowledge
