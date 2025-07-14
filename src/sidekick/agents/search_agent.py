"""
Agno-powered search agent with RAG capabilities.

This module implements an AI agent using the Agno framework that can search
through the RHDH documentation knowledge base and provide intelligent responses.
"""

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
    ):
        """
        Initialize the search agent.

        Args:
            knowledge_path: Path to knowledge documents directory
            storage_path: Path for agent session storage
        """
        # Default storage path
        if storage_path is None:
            storage_path = Path("tmp/agent.db")

        self.storage_path = storage_path
        self.knowledge_manager = KnowledgeManager(knowledge_path=knowledge_path)
        self._agent: Agent | None = None
        self._initialized = False

        logger.debug(f"SearchAgent initialized: storage_path={storage_path}")

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

    def search(self, query: str) -> RunResponse:
        """
        Search using the AI agent and format response for CLI display.

        Args:
            query: Search query string

        Returns:
            Formatted search result string
        """
        # Ensure agent is initialized
        if not self._initialized:
            self.initialize()

        if self._agent is None:
            raise RuntimeError("Agent not properly initialized")

        logger.debug(f"Processing search query: '{query}'")

        # Get response from agent
        response = self._agent.run(query, stream=False)

        return response
