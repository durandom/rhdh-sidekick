"""
Agno-powered search agent with RAG capabilities.

This module implements an AI agent using the Agno framework that can search
through the RHDH documentation knowledge base and provide intelligent responses.
"""

import uuid
from pathlib import Path

from agno.agent import Agent, RunResponse
from agno.models.anthropic import Claude
from agno.storage.sqlite import SqliteStorage
from loguru import logger

from .knowledge import KnowledgeManager


class SearchAgent:
    """AI-powered search agent using Agno framework with RAG capabilities."""

    def __init__(
        self,
        knowledge_path: Path | None = None,
        storage_path: Path | None = None,
        user_id: str | None = None,
    ):
        """
        Initialize the search agent.

        Args:
            knowledge_path: Path to knowledge documents directory
            storage_path: Path for agent session storage
            user_id: Optional user ID for session management
        """
        # Default storage path
        if storage_path is None:
            storage_path = Path("tmp/agent.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self.knowledge_manager = KnowledgeManager(knowledge_path=knowledge_path)
        self._agent: Agent | None = None
        self._initialized = False
        self._session_id: str | None = None

        logger.debug(f"SearchAgent initialized: storage_path={storage_path}, user_id={user_id}")

    def _generate_session_id(self) -> str:
        """Generate a new session ID using UUID."""
        return str(uuid.uuid4())

    def create_session(self, user_id: str | None = None) -> str:
        """
        Create a new session for the agent.

        Args:
            user_id: Optional user ID to override the instance user_id

        Returns:
            The generated session ID
        """
        if user_id is not None:
            self.user_id = user_id

        self._session_id = self._generate_session_id()

        logger.info(f"Created new session: session_id={self._session_id}, user_id={self.user_id}")
        return self._session_id

    def get_current_session(self) -> str | None:
        """
        Get the current session ID.

        Returns:
            Current session ID or None if no session exists
        """
        return self._session_id

    def initialize(self) -> None:
        """Initialize the agent and knowledge base (lazy loading)."""
        if self._initialized:
            logger.debug("Agent already initialized")
            return

        try:
            logger.info("Initializing search agent and knowledge base")

            # Load knowledge base
            knowledge = self.knowledge_manager.load_knowledge(recreate=False)

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Create agent storage
            storage = SqliteStorage(
                table_name="agent_sessions",
                db_file=str(self.storage_path),
            )

            # Create the agent
            self._agent = Agent(
                name="RHDH Search Assistant",
                model=Claude(id="claude-sonnet-4-20250514"),
                instructions=[
                    "Search your knowledge before answering questions.",
                    "Provide concise, helpful responses about Red Hat Developer Hub.",
                    "If asked about Python programming or tutorials, mention relevant RHDH development content.",
                    "Always be direct and focus on the most relevant information.",
                    "Format responses in a clear, structured way.",
                ],
                knowledge=knowledge,
                storage=storage,
                add_datetime_to_instructions=True,
                add_history_to_messages=True,
                num_history_runs=3,
                markdown=True,
            )

            self._initialized = True
            logger.info("Search agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize search agent: {e}")
            self._initialized = False
            raise RuntimeError(f"Agent initialization failed: {e}") from e

    def search(self, query: str, session_id: str | None = None) -> RunResponse:
        """
        Search using the AI agent and format response for CLI display.

        Args:
            query: Search query string
            session_id: Optional session ID to use for this search

        Returns:
            Formatted search result string
        """
        # Ensure agent is initialized
        if not self._initialized:
            self.initialize()

        if self._agent is None:
            raise RuntimeError("Agent not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.debug(f"Processing search query: '{query}' with session_id={self._session_id}")

        # Get response from agent
        response = self._agent.run(query, stream=False, session_id=self._session_id, user_id=self.user_id)

        return response
