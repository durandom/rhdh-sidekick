"""
Jira Knowledge Manager for RAG-based triage.

This module provides a JiraKnowledgeManager class that loads, indexes, and retrieves past Jira issue data
for use in retrieval-augmented generation (RAG) workflows, such as with JiraTriagerAgent.
"""

import json
from pathlib import Path
from typing import Any

from agno.embedder.google import GeminiEmbedder
from agno.knowledge.json import JSONKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from loguru import logger


class JiraKnowledgeManager:
    """Manages Jira issues for RAG-based triage and retrieval."""

    def __init__(
        self,
        data_path: Path | None = None,
        vector_db_path: Path | None = None,
        table_name: str = "jira_issues",
    ):
        """
        Initialize the manager and load/index Jira issues.

        Args:
            data_path: Path to JSON file with Jira issues
            vector_db_path: Path for LanceDB vector storage
            table_name: Name of the LanceDB table
        """
        if data_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            data_path = project_root / "tmp" / "jira_knowledge_base.json"
        if vector_db_path is None:
            vector_db_path = Path("tmp/lancedb")
        self.data_path = data_path
        self.vector_db_path = vector_db_path
        self.table_name = table_name
        self._issues: list[dict[str, Any]] = []
        self._vector_db: LanceDb | None = None
        self._knowledge: JSONKnowledgeBase | None = None
        self._loaded = False
        logger.debug(
            f"JiraKnowledgeManager initialized: data_path={data_path}, "
            f"vector_db_path={vector_db_path}, table_name={table_name}"
        )

    def load_issues(self, recreate: bool = False) -> None:
        """
        Load and index Jira issues from the JSON file into LanceDB for semantic search.

        Args:
            recreate: If True, re-index the data even if already present
        """
        if self._loaded and not recreate:
            logger.debug("Jira issues already loaded and indexed.")
            return
        logger.info(f"Loading Jira issues from {self.data_path}")
        with open(self.data_path) as f:
            self._issues = json.load(f)
        logger.info(f"Loaded {len(self._issues)} Jira issues.")
        # Index issues for semantic search
        self._vector_db = LanceDb(
            uri=str(self.vector_db_path),
            table_name=self.table_name,
            search_type=SearchType.hybrid,
            embedder=GeminiEmbedder(),
        )
        self._knowledge = JSONKnowledgeBase(
            path=self.data_path,
            vector_db=self.get_vector_db(),
            num_documents=5,
        )
        if self._knowledge is not None:
            self._knowledge.load_document(path=self.data_path, recreate=recreate)
        self._loaded = True
        logger.debug("Jira issues indexed for semantic search.")

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
