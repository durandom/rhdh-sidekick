"""
Knowledge base management for RHDH documentation.

This module provides functionality to manage and load the Red Hat Developer Hub
documentation knowledge base using the Agno framework with LanceDB vector storage.
"""

from pathlib import Path

from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from loguru import logger


class KnowledgeManager:
    """Manages RHDH documentation knowledge base with vector storage."""

    def __init__(
        self,
        knowledge_path: Path | None = None,
        vector_db_path: Path | None = None,
        table_name: str = "rhdh_docs",
    ):
        """
        Initialize knowledge manager.

        Args:
            knowledge_path: Path to knowledge documents directory
            vector_db_path: Path for vector database storage
            table_name: Name of the LanceDB table
        """
        # Default paths relative to project root
        if knowledge_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            knowledge_path = project_root / "knowledge" / "rag" / "rhdh"

        if vector_db_path is None:
            vector_db_path = Path("tmp/lancedb")

        self.knowledge_path = knowledge_path
        self.vector_db_path = vector_db_path
        self.table_name = table_name
        self._knowledge: MarkdownKnowledgeBase | None = None
        self._vector_db: LanceDb | None = None

        logger.debug(
            f"KnowledgeManager initialized: knowledge_path={knowledge_path}, "
            f"vector_db_path={vector_db_path}, table_name={table_name}"
        )

    def get_vector_db(self) -> LanceDb:
        """Get or create the LanceDB vector database instance."""
        if self._vector_db is None:
            logger.debug("Creating LanceDB vector database")
            self._vector_db = LanceDb(
                uri=str(self.vector_db_path),
                table_name=self.table_name,
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(
                    id="text-embedding-3-small",
                    dimensions=1536,
                ),
            )
            logger.debug(f"LanceDB created: {self.vector_db_path}/{self.table_name}")
        return self._vector_db

    def load_knowledge(self, recreate: bool = False) -> MarkdownKnowledgeBase:
        """
        Load or create the knowledge base

        Args:
            recreate: If True, recreate the knowledge base even if it exists

        Returns:
            MarkdownKnowledgeBase instance with loaded RHDH docs

        Raises:
            FileNotFoundError: If knowledge path doesn't exist
            RuntimeError: If knowledge loading fails
        """
        if self._knowledge is not None and not recreate:
            logger.debug("Returning existing knowledge base")
            return self._knowledge

        if not self.knowledge_path.exists():
            raise FileNotFoundError(f"Knowledge path not found: {self.knowledge_path}")

        logger.info(f"Loading knowledge base from {self.knowledge_path}")

        try:
            # Create knowledge base from markdown documents
            self._knowledge = MarkdownKnowledgeBase(
                path=self.knowledge_path,
                vector_db=self.get_vector_db(),
            )

            # Load the knowledge base (this will create embeddings if needed)
            logger.debug(f"Loading knowledge base (recreate={recreate})")
            self._knowledge.load(recreate=recreate)

            # Count loaded documents
            doc_count = len(list(self.knowledge_path.rglob("*.md")))
            logger.info(f"Knowledge base loaded successfully: {doc_count} documents")

            return self._knowledge

        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            raise RuntimeError(f"Knowledge loading failed: {e}") from e
