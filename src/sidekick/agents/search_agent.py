"""
Agno-powered search agent with RAG capabilities.

This module implements an AI agent using the Agno framework that can search
through the RHDH documentation knowledge base and provide intelligent responses.
"""

import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from agno.agent import Agent, RunResponse, RunResponseEvent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.knowledge import KnowledgeTools
from agno.tools.reasoning import ReasoningTools
from loguru import logger

from ..knowledge import KnowledgeManager
from .base import BaseAgentFactory


class SearchAgent(BaseAgentFactory):
    """AI-powered search agent using Agno framework with RAG capabilities."""

    def __init__(
        self,
        knowledge_path: Path | None = None,
        storage_path: Path | None = None,
        user_id: str | None = None,
        memory: Any = None,
    ):
        """
        Initialize the search agent.

        Args:
            knowledge_path: Path to knowledge documents directory
            storage_path: Path for agent session storage
            user_id: Optional user ID for session management
            memory: Memory instance for user memory management
        """
        # Default storage path
        if storage_path is None:
            storage_path = self.get_default_storage_path("search")

        super().__init__(storage_path=storage_path, memory=memory)

        self.user_id = user_id
        self.knowledge_manager = KnowledgeManager(knowledge_path=knowledge_path)
        self._agent: Agent | None = None
        self._initialized = False
        self._session_id: str | None = None
        self._knowledge: Any = None  # Will be loaded during setup_context

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

    def get_agent_instructions(self) -> list[str]:
        """Get the instructions for the search agent."""
        # Use the new prompt template system
        return self.get_agent_instructions_from_template(
            knowledge_base_name=getattr(self, "knowledge_base_name", "RHDH documentation"),
            max_search_iterations=getattr(self, "max_search_iterations", 3),
        )

    def get_required_env_vars(self) -> list[str]:
        """Return list of required environment variables."""
        return []  # Search agent doesn't require any environment variables

    async def setup_context(self) -> Any:
        """Setup async context - load knowledge base."""
        logger.info("Loading knowledge base for search agent")
        self._knowledge = await self.knowledge_manager.aload_knowledge(recreate=False)
        return None  # No specific context object needed

    async def cleanup_context(self, context: None) -> None:
        """Cleanup async context - nothing to cleanup for search agent."""
        _ = context  # Unused parameter
        pass

    def create_agent(self, *args, **kwargs) -> Agent:
        """Create and return a configured Agno Agent with search capabilities.

        This method expects the knowledge base to be already loaded via setup_context().

        Args:
            *args: Unused positional arguments
            **kwargs: Unused keyword arguments

        Returns:
            Configured Agent instance
        """
        _ = args  # Unused parameters
        _ = kwargs  # Unused parameters
        if self._knowledge is None:
            raise RuntimeError("Knowledge base not loaded. Call setup_context() first.")

        # Create storage directory if needed
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Create agent storage
        storage = SqliteStorage(
            table_name="search_agent_sessions",
            db_file=str(self.storage_path),
        )

        # Create knowledge tools
        knowledge_tools = KnowledgeTools(
            knowledge=self._knowledge,
            think=True,
            search=True,
            analyze=True,
            add_instructions=True,
            add_few_shot=True,
        )

        # Create the agent
        agent = Agent(
            name="RHDH Search Assistant",
            model=Gemini(id="gemini-2.5-flash"),
            instructions=self.get_agent_instructions(),
            tools=[knowledge_tools, ReasoningTools(add_instructions=True)],
            storage=storage,
            memory=self.memory,
            enable_agentic_memory=bool(self.memory),
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_runs=3,
            add_references=True,
            read_chat_history=True,
            markdown=True,
        )

        return agent

    async def initialize_agent(self) -> Agent:
        """Override to use SearchAgent's existing initialization pattern."""
        # SearchAgent manages its own initialization state
        await self.ainitialize()
        if self._agent is None:
            raise RuntimeError("Failed to initialize search agent")
        return self._agent

    async def ainitialize(self) -> None:
        """Initialize the agent and knowledge base asynchronously (lazy loading)."""
        if self._initialized:
            logger.debug("Agent already initialized")
            return

        try:
            logger.info("Initializing search agent and knowledge base")

            # Setup context (load knowledge base)
            await self.setup_context()

            # Create the agent
            self._agent = self.create_agent()

            self._initialized = True
            logger.info("Search agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize search agent: {e}")
            self._initialized = False
            raise RuntimeError(f"Agent initialization failed: {e}") from e

    def initialize(self) -> None:
        """Initialize the agent and knowledge base (lazy loading).

        Synchronous version kept for backward compatibility.
        """
        if self._initialized:
            logger.debug("Agent already initialized")
            return

        try:
            logger.info("Initializing search agent and knowledge base")

            # Load knowledge base synchronously
            self._knowledge = self.knowledge_manager.load_knowledge(recreate=False)

            # Create the agent
            self._agent = self.create_agent()

            self._initialized = True
            logger.info("Search agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize search agent: {e}")
            self._initialized = False
            raise RuntimeError(f"Agent initialization failed: {e}") from e

    def search(
        self, query: str, session_id: str | None = None, stream: bool = False
    ) -> RunResponse | Iterator[RunResponseEvent]:
        """
        Search using the AI agent and format response for CLI display.

        Args:
            query: Search query string
            session_id: Optional session ID to use for this search
            stream: Whether to return streaming response

        Returns:
            RunResponse or Iterator[RunResponseEvent] for streaming
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
        if stream:
            response_stream = self._agent.run(
                query,
                stream=True,
                stream_intermediate_steps=True,
                session_id=self._session_id,
                user_id=self.user_id,
            )
            return response_stream
        else:
            response = self._agent.run(query, stream=False, session_id=self._session_id, user_id=self.user_id)
            return response
