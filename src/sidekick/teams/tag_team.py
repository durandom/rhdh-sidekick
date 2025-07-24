"""
Tag Team with Jira, GitHub, and Search agents for collaborative ticket, PR, and knowledge management.

This module implements a coordinate mode team that combines Jira ticket management,
GitHub repository operations, and knowledge base searches using specialized agents.
"""

import uuid
from pathlib import Path
from typing import Any

from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.team import Team, TeamRunResponse
from agno.tools.mcp import MCPTools
from loguru import logger

from ..agents.github_agent import GitHubAgent
from ..agents.jira_agent import JiraAgent
from ..agents.search_agent import SearchAgent
from ..prompts import get_prompt_registry
from ..tools.state_management import StateManagementToolkit


class TagTeam:
    """Coordinate mode team for Jira, GitHub, and knowledge base integration using specialized agents."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
        repository: str | None = None,
        knowledge_path: Path | None = None,
        memory: Memory | None = None,
    ):
        """
        Initialize the tag team.

        Args:
            storage_path: Path for team session storage
            user_id: Optional user ID for session management
            repository: Default GitHub repository (format: "owner/repo")
            knowledge_path: Path to knowledge documents directory for SearchAgent
            memory: Memory instance for shared memory across all team members
        """
        if storage_path is None:
            storage_path = Path("tmp/sidekick.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self.repository = repository
        self.knowledge_path = knowledge_path
        self.memory = memory
        self._team: Team | None = None
        self._initialized = False
        self._session_id: str | None = None
        self._jira_mcp_tools: MCPTools | None = None
        self._github_tools: Any | None = None
        self._search_agent: SearchAgent | None = None

        logger.debug(
            f"TagTeam initialized: storage_path={storage_path}, user_id={user_id}, "
            f"repository={repository}, knowledge_path={knowledge_path}"
        )

    def _generate_session_id(self) -> str:
        """Generate a new session ID using UUID."""
        return str(uuid.uuid4())

    def create_session(self, user_id: str | None = None) -> str:
        """
        Create a new session for the team.

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

    def get_team_instructions(self) -> list[str]:
        """
        Get team instructions from the prompt template.

        Returns:
            List of instruction strings for the team coordinator
        """
        registry = get_prompt_registry()
        template = registry.get("teams.tag_team")
        return template.get_instructions_list(team_name=self.__class__.__name__)

    def get_member_coordination_instructions(self, member_role: str) -> list[str]:
        """
        Get coordination instructions for team members.

        Args:
            member_role: The role description for the team member

        Returns:
            List of coordination instruction strings
        """
        registry = get_prompt_registry()
        template = registry.get("teams.team_member_coordination")
        return template.get_instructions_list(member_role=member_role)

    def clear_memory(self) -> None:
        """Clear the shared memory for all agents and team."""
        if self.memory is not None:
            self.memory.clear()
            logger.info("Cleared tag team memory")

    async def __aenter__(self):
        """Async context manager entry - initializes MCP tools."""
        await self._setup_mcp_context()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleans up MCP tools."""
        _ = exc_type, exc_val, exc_tb  # Unused parameters
        await self._cleanup_mcp_context()

    async def _setup_mcp_context(self) -> None:
        """Set up MCP tools within proper async context."""
        logger.info("Setting up MCP context for tag team")

        # Create Jira MCP tools
        jira_agent_factory = JiraAgent(memory=self.memory)
        self._jira_mcp_tools = jira_agent_factory.create_mcp_tools()

        # Create GitHub tools
        github_agent_factory = GitHubAgent(repository=self.repository, memory=self.memory)
        self._github_tools = github_agent_factory.create_github_tools()

        # Create SearchAgent (no MCP context needed)
        self._search_agent = SearchAgent(
            knowledge_path=self.knowledge_path, storage_path=self.storage_path, memory=self.memory
        )

        # Start MCP context
        if self._jira_mcp_tools is not None:
            await self._jira_mcp_tools.__aenter__()

        logger.info("MCP context setup completed")

    async def _cleanup_mcp_context(self) -> None:
        """Clean up MCP tools context."""
        logger.info("Cleaning up MCP context")

        if self._jira_mcp_tools:
            try:
                await self._jira_mcp_tools.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error cleaning up Jira MCP tools: {e}")

        logger.info("MCP context cleanup completed")

    async def initialize(self) -> None:
        """Initialize the team with Jira and GitHub agents."""
        if self._initialized:
            logger.debug("Team already initialized")
            return

        if self._jira_mcp_tools is None or self._github_tools is None or self._search_agent is None:
            raise RuntimeError("MCP context not set up. Use TagTeam as async context manager.")

        try:
            logger.info("Initializing tag team")

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Use provided memory or create fallback memory for persistent chat history
            if self.memory is None:
                self.memory = Memory()

            # Create team storage
            storage = SqliteStorage(
                table_name="tag_team_sessions",
                db_file=str(self.storage_path),
            )

            # Create Jira agent using the factory pattern with MCP tools from context
            jira_agent_factory = JiraAgent(memory=self.memory)
            jira_agent = jira_agent_factory.create_agent(self._jira_mcp_tools)

            # Update Jira agent for team coordination and add shared memory
            jira_agent.name = "Jira Specialist"
            jira_agent.role = "Manages Jira tickets, searches issues, and extracts ticket information"
            jira_agent.memory = self.memory  # Add shared memory for chat history

            # Get original instructions and add team coordination instructions
            original_instructions = jira_agent_factory.get_agent_instructions()
            team_instructions = self.get_member_coordination_instructions(
                "ticket information for GitHub operations, "
                "Jira issues to GitHub PRs connections, "
                "and business requirements from tickets"
            )
            jira_agent.instructions = original_instructions + team_instructions

            # Create GitHub agent using the factory pattern with tools from context
            github_agent_factory = GitHubAgent(repository=self.repository, memory=self.memory)
            github_agent = github_agent_factory.create_agent(self._github_tools)

            # Update GitHub agent for team coordination and add shared memory
            github_agent.name = "GitHub Specialist"
            github_agent.role = "Manages GitHub repositories, pull requests, and code analysis"
            github_agent.memory = self.memory  # Add shared memory for chat history

            # Get original instructions and add team coordination instructions
            original_instructions = github_agent_factory.get_agent_instructions()
            team_instructions = self.get_member_coordination_instructions(
                "GitHub PRs to Jira tickets connections, "
                "technical context about code changes, "
                "and relevant repository identification"
            )
            github_agent.instructions = original_instructions + team_instructions

            # Initialize SearchAgent and create agent for team
            search_agent = await self._search_agent.initialize_agent()

            # Update SearchAgent for team coordination and add shared memory
            search_agent.name = "Knowledge Specialist"
            search_agent.role = (
                "Searches documentation, provides knowledge base insights, and answers technical questions"
            )
            search_agent.memory = self.memory  # Add shared memory for chat history

            # Get original instructions and add team coordination instructions
            original_instructions = self._search_agent.get_agent_instructions()
            team_instructions = self.get_member_coordination_instructions(
                "documentation context for Jira tickets and GitHub issues, "
                "relevant technical knowledge to support decisions, "
                "and best practices/implementation guidance"
            )
            search_agent.instructions = original_instructions + team_instructions

            # Initialize team session state for shared context tracking
            from datetime import datetime

            team_session_state: dict[str, Any] = {
                "analyzed_tickets": [],
                "analyzed_prs": [],
                "ticket_pr_links": {},
                "current_investigation": None,
                "user_preferences": {},
                "session_start_time": datetime.now().isoformat(),
            }

            # Team's private session state for metrics and coordination
            team_private_state: dict[str, Any] = {
                "coordination_actions": [],
                "specialist_interactions": 0,
                "session_metrics": {},
            }

            # Create async state management toolkit for the team
            state_toolkit = StateManagementToolkit(team_session_state)

            # Create the coordinate mode team
            self._team = Team(
                name="Tag Team",
                mode="coordinate",
                model=Gemini(id="gemini-2.5-flash"),
                members=[jira_agent, github_agent, search_agent],
                description=(
                    "A specialized team for coordinating Jira ticket management, "
                    "GitHub repository operations, and knowledge base searches"
                ),
                instructions=self.get_team_instructions(),
                tools=[state_toolkit],
                team_session_state=team_session_state,  # Shared state for all team members
                session_state=team_private_state,  # Team leader's private state
                storage=storage,
                memory=self.memory,  # Add shared memory for persistent chat history
                enable_agentic_memory=True,
                add_datetime_to_instructions=True,
                enable_agentic_context=True,
                enable_team_history=True,  # Enable chat history within sessions
                share_member_interactions=True,
                show_members_responses=True,
                markdown=True,
            )

            self._initialized = True
            logger.info("Tag team initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize tag team: {e}")
            self._initialized = False
            raise RuntimeError(f"Team initialization failed: {e}") from e

    async def run(self, query: str, session_id: str | None = None) -> TeamRunResponse:
        """
        Run a query against the tag team.

        Note: This method assumes TagTeam is being used within an async context manager.

        Args:
            query: Question or task for the team
            session_id: Optional session ID to use for this query

        Returns:
            Team response with coordinated analysis
        """
        if not self._initialized:
            await self.initialize()

        if self._team is None:
            raise RuntimeError("Team not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.info(f"Processing query: '{query}' with session_id={self._session_id}")

        # Get response from team
        response = self._team.run(query, session_id=self._session_id, user_id=self.user_id)

        return response

    async def acli_app(
        self,
        message: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        user: str = "User",
        emoji: str = ":label:",
        stream: bool = False,
        markdown: bool = False,
        exit_on: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Run an interactive command-line interface to interact with the tag team.
        Works with team dependencies requiring async logic.

        Note: This method assumes TagTeam is being used within an async context manager.

        Args:
            message: Initial message to send
            session_id: Optional session ID to use
            user_id: Optional user ID for session management
            user: User identifier for display
            emoji: Emoji to use in prompts
            stream: Whether to stream responses
            markdown: Whether to render markdown
            exit_on: List of exit commands
            **kwargs: Additional arguments
        """
        from rich.prompt import Prompt

        if not self._initialized:
            await self.initialize()

        if self._team is None:
            raise RuntimeError("Team not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session(user_id)

        # Use provided user_id or keep existing
        if user_id is not None:
            self.user_id = user_id

        if message:
            await self.aprint_response(
                message=message, stream=stream, markdown=markdown, session_id=self._session_id, **kwargs
            )

        _exit_on = exit_on or ["exit", "quit", "bye"]
        while True:
            message = Prompt.ask(f"[bold] {emoji} {user} [/bold]")
            if message in _exit_on:
                break

            await self.aprint_response(
                message=message, stream=stream, markdown=markdown, session_id=self._session_id, **kwargs
            )

    async def aprint_response(
        self,
        message: str,
        stream: bool = False,
        markdown: bool = False,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Print the team's response to a message with proper formatting.
        Uses the Team's built-in aprint_response method.

        Note: This method assumes TagTeam is being used within an async context manager.

        Args:
            message: The message to send to the team
            stream: Whether to stream the response
            markdown: Whether to render markdown
            session_id: Optional session ID to use
            **kwargs: Additional arguments
        """
        if self._team is None:
            raise RuntimeError("Team not properly initialized")

        # Use the team's built-in aprint_response method which handles formatting
        await self._team.aprint_response(
            message=message,
            stream=stream,
            markdown=markdown,
            session_id=session_id or self._session_id,
            user_id=self.user_id,
            **kwargs,
        )
