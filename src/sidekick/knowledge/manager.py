"""
Knowledge base management for RHDH documentation.

This module provides functionality to manage and load the Red Hat Developer Hub
documentation knowledge base using the Agno framework with LanceDB vector storage.
Supports both markdown and PDF documents.
"""

import asyncio
from pathlib import Path

from agno.embedder.google import GeminiEmbedder
from agno.knowledge import AgentKnowledge
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.lancedb import LanceDb, SearchType
from loguru import logger


class KnowledgeManager:
    """Manages RHDH documentation knowledge base with vector storage for both markdown and PDF files."""

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
        # Default paths relative to project root - use entire knowledge directory
        if knowledge_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            knowledge_path = project_root / "knowledge"

        if vector_db_path is None:
            vector_db_path = Path("tmp/lancedb")

        self.knowledge_path = knowledge_path
        self.vector_db_path = vector_db_path
        self.table_name = table_name
        self._knowledge: AgentKnowledge | None = None
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
                embedder=GeminiEmbedder(),
            )
            logger.debug(f"LanceDB created: {self.vector_db_path}/{self.table_name}")
        return self._vector_db

    def check_table_exists(self) -> bool:
        """
        Check if the LanceDB table exists and has data.

        Returns:
            True if table exists and has data, False otherwise
        """
        try:
            vector_db = self.get_vector_db()
            # Try to access the table row count
            if hasattr(vector_db, "table") and vector_db.table is not None:
                row_count = vector_db.table.count_rows()
                logger.debug(f"Table {self.table_name} exists with {row_count} rows")
                return bool(row_count > 0)
            return False
        except Exception as e:
            logger.debug(f"Table check failed: {e}")
            return False

    async def reindex(self) -> None:
        """
        Reindex the knowledge base by recreating the vector database.

        This will reload all documents and rebuild the vector embeddings.
        """
        logger.info("Starting knowledge base reindexing...")

        try:
            # Force reload the knowledge base
            await self.aload_knowledge(recreate=True, force_reload=True)
            logger.info("Knowledge base reindexing completed successfully")
        except Exception as e:
            logger.error(f"Failed to reindex knowledge base: {e}")
            raise RuntimeError(f"Reindexing failed: {e}") from e

    def reindex_sync(self) -> None:
        """
        Reindex the knowledge base synchronously.

        This is a synchronous wrapper around the async reindex method.
        """
        asyncio.run(self.reindex())

    async def aload_knowledge(self, recreate: bool = False, force_reload: bool = False) -> AgentKnowledge:
        """
        Load or create the knowledge base asynchronously.

        Args:
            recreate: If True, recreate the knowledge base even if it exists
            force_reload: If True, reload documents even if table exists

        Returns:
            AgentKnowledge instance with loaded RHDH docs (markdown + PDF)

        Raises:
            FileNotFoundError: If knowledge path doesn't exist
            RuntimeError: If knowledge loading fails
        """
        if self._knowledge is not None and not recreate:
            logger.debug("Returning existing knowledge base")
            return self._knowledge

        if not self.knowledge_path.exists():
            raise FileNotFoundError(f"Knowledge path not found: {self.knowledge_path}")

        try:
            # Get the shared vector database instance
            vector_db = self.get_vector_db()
            self._vector_db = vector_db

            # Check if table exists and has data
            table_exists = self.check_table_exists()

            if table_exists and not recreate and not force_reload:
                logger.info(
                    f"LanceDB table '{self.table_name}' already exists with data. "
                    "Skipping document loading for faster startup."
                )

                # Count documents for reference
                md_files = list(self.knowledge_path.rglob("*.md"))
                pdf_files = list(self.knowledge_path.rglob("*.pdf"))

                # Create knowledge base object without loading documents
                if pdf_files:
                    logger.debug("Creating PDFKnowledgeBase (without loading)")
                    self._knowledge = PDFKnowledgeBase(
                        path=self.knowledge_path,
                        vector_db=vector_db,
                        reader=PDFReader(chunk=True),
                    )
                else:
                    logger.debug("Creating MarkdownKnowledgeBase (without loading)")
                    self._knowledge = MarkdownKnowledgeBase(
                        path=self.knowledge_path,
                        vector_db=vector_db,
                    )

                logger.info(
                    f"Knowledge base ready (using existing data). "
                    f"Available: {len(md_files)} markdown and {len(pdf_files)} PDF files"
                )

                return self._knowledge

            # Table doesn't exist or force_reload requested - load documents
            logger.info(f"Loading knowledge base from {self.knowledge_path}")

            # Count documents first
            md_files = list(self.knowledge_path.rglob("*.md"))
            pdf_files = list(self.knowledge_path.rglob("*.pdf"))

            if not md_files and not pdf_files:
                raise RuntimeError(f"No supported documents found in {self.knowledge_path}")

            logger.debug(f"Found {len(md_files)} markdown and {len(pdf_files)} PDF files")

            # Prioritize PDF files since they contain the team documentation
            if pdf_files:
                logger.info("Using PDFKnowledgeBase to process PDF documents")
                self._knowledge = PDFKnowledgeBase(
                    path=self.knowledge_path,
                    vector_db=vector_db,
                    reader=PDFReader(chunk=True),
                )
            else:
                logger.info("Using MarkdownKnowledgeBase to process markdown documents")
                self._knowledge = MarkdownKnowledgeBase(
                    path=self.knowledge_path,
                    vector_db=vector_db,
                )

            # Load the knowledge base asynchronously
            logger.debug(f"Loading knowledge base asynchronously (recreate={recreate})")
            await self._knowledge.aload(recreate=recreate)

            # Count loaded documents by checking what was actually processed
            logger.info(
                f"Knowledge base loaded successfully with {len(md_files)} markdown "
                f"and {len(pdf_files)} PDF files available"
            )

            return self._knowledge

        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            raise RuntimeError(f"Knowledge loading failed: {e}") from e

    def load_knowledge(self, recreate: bool = False, force_reload: bool = False) -> AgentKnowledge:
        """
        Load or create the knowledge base (synchronous wrapper for async method).

        Args:
            recreate: If True, recreate the knowledge base even if it exists
            force_reload: If True, reload documents even if table exists

        Returns:
            AgentKnowledge instance with loaded RHDH docs (markdown + PDF)

        Raises:
            FileNotFoundError: If knowledge path doesn't exist
            RuntimeError: If knowledge loading fails
        """
        return asyncio.run(self.aload_knowledge(recreate=recreate, force_reload=force_reload))
