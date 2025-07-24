"""
Agno-powered search agent with RAG capabilities.

This module implements an AI agent using the Agno framework that can search
through the RHDH documentation knowledge base and provide intelligent responses.
"""

import uuid
from collections.abc import Iterator
from pathlib import Path

from agno.agent import Agent, RunResponse, RunResponseEvent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.reasoning import ReasoningTools
from loguru import logger

from ..knowledge import KnowledgeManager


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

    async def ainitialize(self) -> None:
        """Initialize the agent and knowledge base asynchronously (lazy loading)."""
        if self._initialized:
            logger.debug("Agent already initialized")
            return

        try:
            logger.info("Initializing search agent and knowledge base")

            # Load knowledge base asynchronously
            knowledge = await self.knowledge_manager.aload_knowledge(recreate=False)

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
                model=Gemini(id="gemini-2.5-flash"),
                instructions=[
                    "CRITICAL KNOWLEDGE BASE SEARCH REQUIREMENT:",
                    "You MUST ALWAYS search your knowledge base using the search_knowledge_base tool "
                    "before providing any answer to any question, regardless of how simple or obvious "
                    "the question may seem. This is a mandatory first step that cannot be skipped.",
                    "",
                    "AUDIENCE AND TECHNICAL FOCUS:",
                    "Your primary audience consists of engineers and technical professionals who need "
                    "precise, actionable technical data. Prioritize technical accuracy, implementation "
                    "details, and practical guidance over general explanations.",
                    "",
                    "SEARCH PROCESS:",
                    "1. ALWAYS perform a comprehensive knowledge base search first using relevant keywords",
                    "2. Use multiple search queries if the initial search doesn't yield sufficient results",
                    "3. Search for both specific terms and broader contextual information",
                    "4. Never rely on your pre-existing knowledge without first consulting the knowledge base",
                    "",
                    "RESPONSE REQUIREMENTS:",
                    "- Provide detailed, comprehensive responses based on search results",
                    "- Include all relevant information found in the knowledge base - do not summarize "
                    "or shorten unnecessarily",
                    "- Preserve important details, examples, code snippets, and procedural steps from "
                    "the documentation",
                    "- When multiple relevant documents are found, synthesize information from all sources",
                    "- Always cite specific document sources with titles or filenames when available",
                    "",
                    "CONTENT HANDLING:",
                    "- For Red Hat Developer Hub (RHDH) questions, provide thorough explanations with "
                    "all available context",
                    "- For Python programming or development tutorials, search extensively for "
                    "RHDH-specific development content",
                    "- Include configuration examples, code samples, and step-by-step procedures when found",
                    "- Preserve technical specifications, version requirements, and compatibility information",
                    "- Focus on implementation details, API references, and troubleshooting information",
                    "",
                    "NO RESULTS HANDLING:",
                    "If searches return no relevant results, clearly state: 'No information was found "
                    "in the knowledge base for this query.'",
                    "Then suggest alternative search terms or related topics that might be available.",
                    "",
                    "FORMATTING STANDARDS:",
                    "- Structure responses with clear headings and sections",
                    "- Use bullet points or numbered lists for procedural information",
                    "- Format code blocks and configuration examples properly",
                    "- Maintain the original context and meaning from source documents",
                    "- Ensure responses are complete and self-contained with all necessary details",
                ],
                knowledge=knowledge,
                tools=[ReasoningTools(add_instructions=True)],
                storage=storage,
                add_datetime_to_instructions=True,
                add_history_to_messages=True,
                num_history_runs=3,
                add_references=True,
                search_knowledge=True,
                read_chat_history=True,
                markdown=True,
            )

            self._initialized = True
            logger.info("Search agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize search agent: {e}")
            self._initialized = False
            raise RuntimeError(f"Agent initialization failed: {e}") from e

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
                model=Gemini(id="gemini-2.5-flash"),
                instructions=[
                    "CRITICAL KNOWLEDGE BASE SEARCH REQUIREMENT:",
                    "You MUST ALWAYS search your knowledge base using the search_knowledge_base tool "
                    "before providing any answer to any question, regardless of how simple or obvious "
                    "the question may seem. This is a mandatory first step that cannot be skipped.",
                    "",
                    "AUDIENCE AND TECHNICAL FOCUS:",
                    "Your primary audience consists of engineers and technical professionals who need "
                    "precise, actionable technical data. Prioritize technical accuracy, implementation "
                    "details, and practical guidance over general explanations.",
                    "",
                    "SEARCH PROCESS:",
                    "1. ALWAYS perform a comprehensive knowledge base search first using relevant keywords",
                    "2. Use multiple search queries if the initial search doesn't yield sufficient results",
                    "3. Search for both specific terms and broader contextual information",
                    "4. Never rely on your pre-existing knowledge without first consulting the knowledge base",
                    "",
                    "RESPONSE REQUIREMENTS:",
                    "- Provide detailed, comprehensive responses based on search results",
                    "- Include all relevant information found in the knowledge base - do not summarize "
                    "or shorten unnecessarily",
                    "- Preserve important details, examples, code snippets, and procedural steps from "
                    "the documentation",
                    "- When multiple relevant documents are found, synthesize information from all sources",
                    "- Always cite specific document sources with titles or filenames when available",
                    "",
                    "CONTENT HANDLING:",
                    "- For Red Hat Developer Hub (RHDH) questions, provide thorough explanations with "
                    "all available context",
                    "- For Python programming or development tutorials, search extensively for "
                    "RHDH-specific development content",
                    "- Include configuration examples, code samples, and step-by-step procedures when found",
                    "- Preserve technical specifications, version requirements, and compatibility information",
                    "- Focus on implementation details, API references, and troubleshooting information",
                    "",
                    "NO RESULTS HANDLING:",
                    "If searches return no relevant results, clearly state: 'No information was found "
                    "in the knowledge base for this query.'",
                    "Then suggest alternative search terms or related topics that might be available.",
                    "",
                    "FORMATTING STANDARDS:",
                    "- Structure responses with clear headings and sections",
                    "- Use bullet points or numbered lists for procedural information",
                    "- Format code blocks and configuration examples properly",
                    "- Maintain the original context and meaning from source documents",
                    "- Ensure responses are complete and self-contained with all necessary details",
                ],
                knowledge=knowledge,
                tools=[ReasoningTools(add_instructions=True)],
                storage=storage,
                add_datetime_to_instructions=True,
                add_history_to_messages=True,
                num_history_runs=3,
                add_references=True,
                search_knowledge=True,
                read_chat_history=True,
                markdown=True,
            )

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
