"""
Knowledge base management for RHDH documentation.

This module provides functionality to manage and load the Red Hat Developer Hub
documentation knowledge base using the Agno framework with LanceDB vector storage.
Supports both markdown and PDF documents.
"""

import asyncio
from pathlib import Path

from agno.document.chunking.markdown import MarkdownChunking
from agno.document.reader.markdown_reader import MarkdownReader
from agno.document.reader.pdf_reader import PDFReader
from agno.embedder.google import GeminiEmbedder
from agno.knowledge import AgentKnowledge
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.markdown import MarkdownKnowledgeBase
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from loguru import logger

from .chunking import FixedSizeChunking


class KnowledgeManager:
    """Manages RHDH documentation knowledge base with vector storage for markdown, PDF, and CSV files."""

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
                embedder=GeminiEmbedder(id="gemini-embedding-001"),
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

    def _count_documents(self) -> tuple[list[Path], list[Path], list[Path]]:
        """Count and return markdown, PDF, and CSV files in the knowledge path."""
        md_files = list(self.knowledge_path.rglob("*.md"))
        pdf_files = list(self.knowledge_path.rglob("*.pdf"))
        csv_files = list(self.knowledge_path.rglob("*.csv"))
        return md_files, pdf_files, csv_files

    def _create_knowledge_base(
        self, vector_db: LanceDb, md_files: list[Path], pdf_files: list[Path], csv_files: list[Path]
    ) -> AgentKnowledge:
        """Create appropriate knowledge base instance based on available files."""
        # Create chunking strategy with 20,000 character chunks
        chunking_strategy = FixedSizeChunking(chunk_size=20000, overlap=200)

        sources: list[AgentKnowledge] = []

        # Add markdown knowledge base if we have markdown files
        if md_files:
            logger.debug("Adding MarkdownKnowledgeBase to combined knowledge base")
            md_kb = MarkdownKnowledgeBase(
                path=self.knowledge_path,
                vector_db=vector_db,
                chunking_strategy=chunking_strategy,
                num_documents=5,
                reader=MarkdownReader(chunking_strategy=MarkdownChunking(chunk_size=1000000, overlap=200)),
            )
            sources.append(md_kb)

        # Add PDF knowledge base if we have PDF files
        if pdf_files:
            logger.debug("Adding PDFKnowledgeBase to combined knowledge base")
            pdf_kb = PDFKnowledgeBase(
                path=self.knowledge_path,
                vector_db=vector_db,
                reader=PDFReader(chunk=True),
                chunking_strategy=chunking_strategy,
            )
            sources.append(pdf_kb)

        # Add CSV knowledge base if we have CSV files
        if csv_files:
            logger.debug("Adding CSVKnowledgeBase to combined knowledge base")
            csv_kb = CSVKnowledgeBase(
                path=self.knowledge_path,
                vector_db=vector_db,
            )
            sources.append(csv_kb)

        logger.debug(f"Creating CombinedKnowledgeBase with {len(sources)} sources")
        return CombinedKnowledgeBase(
            sources=sources,
            vector_db=vector_db,
            num_documents=5,
        )

    async def aload_knowledge(self, recreate: bool = False, force_reload: bool = False) -> AgentKnowledge:
        """
        Load or create the knowledge base asynchronously.

        Args:
            recreate: If True, recreate the knowledge base even if it exists
            force_reload: If True, reload documents even if table exists

        Returns:
            AgentKnowledge instance with loaded RHDH docs (markdown + PDF + CSV)

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

            # Count documents for reference
            md_files, pdf_files, csv_files = self._count_documents()

            if not md_files and not pdf_files and not csv_files:
                raise RuntimeError(f"No supported documents found in {self.knowledge_path}")

            # Check if table exists and has data
            table_exists = self.check_table_exists()

            if table_exists and not recreate and not force_reload:
                logger.info(
                    f"LanceDB table '{self.table_name}' already exists with data. "
                    "Skipping document loading for faster startup."
                )

                # Create knowledge base object without loading documents
                self._knowledge = self._create_knowledge_base(vector_db, md_files, pdf_files, csv_files)

                logger.info(
                    f"Knowledge base ready (using existing data). "
                    f"Available: {len(md_files)} markdown, {len(pdf_files)} PDF, and {len(csv_files)} CSV files"
                )

                return self._knowledge

            # Table doesn't exist or force_reload requested - load documents
            logger.info(f"Loading knowledge base from {self.knowledge_path}")
            logger.debug(f"Found {len(md_files)} markdown, {len(pdf_files)} PDF, and {len(csv_files)} CSV files")

            # Create and load knowledge base
            self._knowledge = self._create_knowledge_base(vector_db, md_files, pdf_files, csv_files)

            logger.info("Using CombinedKnowledgeBase to process document types")

            # Load the knowledge base asynchronously
            logger.debug(f"Loading knowledge base asynchronously (recreate={recreate})")
            await self._knowledge.aload(recreate=recreate)

            logger.info(
                f"Knowledge base loaded successfully with {len(md_files)} markdown, "
                f"{len(pdf_files)} PDF, and {len(csv_files)} CSV files available"
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
            AgentKnowledge instance with loaded RHDH docs (markdown + PDF + CSV)

        Raises:
            FileNotFoundError: If knowledge path doesn't exist
            RuntimeError: If knowledge loading fails
        """
        return asyncio.run(self.aload_knowledge(recreate=recreate, force_reload=force_reload))
