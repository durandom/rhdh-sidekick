"""
Tag Team with Jira and GitHub agents for collaborative ticket and PR management.

This module implements a coordinate mode team that combines Jira ticket management
with GitHub repository operations using specialized agents.
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
from ..tools.state_management import StateManagementToolkit


class TagTeam:
    """Coordinate mode team for Jira and GitHub integration using specialized agents."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
        repository: str | None = None,
    ):
        """
        Initialize the tag team.

        Args:
            storage_path: Path for team session storage
            user_id: Optional user ID for session management
            repository: Default GitHub repository (format: "owner/repo")
        """
        if storage_path is None:
            storage_path = Path("tmp/tag_team.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self.repository = repository
        self._team: Team | None = None
        self._initialized = False
        self._session_id: str | None = None
        self._memory: Memory | None = None
        self._jira_mcp_tools: MCPTools | None = None
        self._github_tools: Any | None = None

        logger.debug(f"TagTeam initialized: storage_path={storage_path}, user_id={user_id}, repository={repository}")

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

    def clear_memory(self) -> None:
        """Clear the shared memory for all agents and team."""
        if self._memory is not None:
            self._memory.clear()
            logger.info("Cleared tag team memory")

    async def __aenter__(self):
        """Async context manager entry - initializes MCP tools."""
        await self._setup_mcp_context()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleans up MCP tools."""
        await self._cleanup_mcp_context()

    async def _setup_mcp_context(self) -> None:
        """Set up MCP tools within proper async context."""
        logger.info("Setting up MCP context for tag team")

        # Create Jira MCP tools
        jira_agent_factory = JiraAgent()
        self._jira_mcp_tools = jira_agent_factory.create_mcp_tools()

        # Create GitHub tools
        github_agent_factory = GitHubAgent(repository=self.repository)
        self._github_tools = github_agent_factory.create_github_tools()

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

        if self._jira_mcp_tools is None or self._github_tools is None:
            raise RuntimeError("MCP context not set up. Use TagTeam as async context manager.")

        try:
            logger.info("Initializing tag team")

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Create shared memory for persistent chat history
            self._memory = Memory()

            # Create team storage
            storage = SqliteStorage(
                table_name="tag_team_sessions",
                db_file=str(self.storage_path),
            )

            # Create Jira agent using the factory pattern with MCP tools from context
            jira_agent_factory = JiraAgent()
            jira_agent = jira_agent_factory.create_agent(self._jira_mcp_tools)

            # Update Jira agent for team coordination and add shared memory
            jira_agent.name = "Jira Specialist"
            jira_agent.role = "Manages Jira tickets, searches issues, and extracts ticket information"
            jira_agent.memory = self._memory  # Add shared memory for chat history

            # Get original instructions and add team coordination instructions
            original_instructions = jira_agent_factory.get_agent_instructions()
            team_instructions = [
                "When working with other team members:",
                "- Share relevant ticket information for GitHub operations",
                "- Connect Jira issues to GitHub PRs when requested",
                "- Provide context about business requirements from tickets",
                "- Use the shared team session state to track your analysis work",
                "- The team will have generic state management tools you can request",
                "Be concise but thorough in your responses to support team coordination.",
            ]
            jira_agent.instructions = original_instructions + team_instructions

            # Create GitHub agent using the factory pattern with tools from context
            github_agent_factory = GitHubAgent(repository=self.repository)
            github_agent = github_agent_factory.create_agent(self._github_tools)

            # Update GitHub agent for team coordination and add shared memory
            github_agent.name = "GitHub Specialist"
            github_agent.role = "Manages GitHub repositories, pull requests, and code analysis"
            github_agent.memory = self._memory  # Add shared memory for chat history

            # Get original instructions and add team coordination instructions
            original_instructions = github_agent_factory.get_agent_instructions()
            team_instructions = [
                "When working with other team members:",
                "- Connect GitHub PRs to Jira tickets when requested",
                "- Provide technical context about code changes",
                "- Help identify relevant repositories for specific tasks",
                "- Use the shared team session state to track your analysis work",
                "- The team will have generic state management tools you can request",
                "Be concise but thorough in your responses to support team coordination.",
            ]
            github_agent.instructions = original_instructions + team_instructions

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
                members=[jira_agent, github_agent],
                description=(
                    "A specialized team for coordinating Jira ticket management with GitHub repository operations"
                ),
                instructions=[
                    "You are the team leader coordinating between Jira and GitHub operations.",
                    "Your team consists of two specialists:",
                    "1. Jira Specialist - handles ticket management, searches, and analysis",
                    "2. GitHub Specialist - handles repository operations, PR analysis, and code review",
                    "Your coordination strategy:",
                    "1. Analyze user requests to determine which specialists are needed",
                    "2. For ticket-related queries, delegate to the Jira Specialist first",
                    "3. For repository or PR queries, delegate to the GitHub Specialist",
                    "4. For cross-platform tasks (linking tickets to PRs), coordinate both specialists",
                    "5. Synthesize responses from both specialists into coherent answers",
                    "Common coordination patterns:",
                    "- Ticket analysis: Get ticket details from Jira, then find related PRs in GitHub",
                    "- PR review: Get PR details from GitHub, then check for linked Jira tickets",
                    "- Feature tracking: Connect Jira feature tickets to GitHub implementation PRs",
                    "- Bug investigation: Link Jira bug reports to GitHub fixes and code changes",
                    "Available generic state management tools:",
                    "- set_state_value: Set any value in the session state",
                    "- track_item: Track items in collections (tickets, PRs, etc.)",
                    "- link_items: Create relationships between any items",
                    "- get_state_summary: Get a summary of the current session state",
                    "Use these tools creatively to track progress, maintain context, and coordinate work.",
                    "Always provide clear, actionable responses that leverage insights from both platforms.",
                    "When information is requested from both platforms, ensure responses are well-integrated.",
                    "You have access to the conversation history and shared session state.",
                    "Use the session context to avoid redundant analysis and build on previous work.",
                ],
                tools=[state_toolkit],
                team_session_state=team_session_state,  # Shared state for all team members
                session_state=team_private_state,  # Team leader's private state
                storage=storage,
                memory=self._memory,  # Add shared memory for persistent chat history
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
