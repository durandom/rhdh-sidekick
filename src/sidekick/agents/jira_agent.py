"""
Jira integration agent for fetching ticket information.

This module implements an AI agent using the Agno framework that can interact
with Jira to fetch ticket details and extract relevant information.
Supports both JiraTools and MCP Atlassian server integration.
"""

import uuid
from os import getenv
from pathlib import Path

from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.mcp import MCPTools
from loguru import logger

from sidekick.tools.jira import JiraIssueData, jira_get_issue, jira_search_issues

# Using JiraIssueData from tools.jira instead of local JiraIssue
# This ensures consistency with the existing Pydantic model


class JiraAgent:
    """AI-powered Jira agent using Agno framework for ticket processing."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
        use_mcp: bool = True,
        use_structured_output: bool = False,
    ):
        """
        Initialize the Jira agent.

        Args:
            storage_path: Path for agent session storage
            user_id: Optional user ID for session management
            use_mcp: Whether to use MCP Atlassian server (True) or JiraTools (False)
            use_structured_output: Whether to use structured output with response_model (False by default)
        """
        # Default storage path
        if storage_path is None:
            storage_path = Path("tmp/jira_agent.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self.use_mcp = use_mcp
        self.use_structured_output = use_structured_output
        self._agent: Agent | None = None
        self._initialized = False
        self._session_id: str | None = None
        self._mcp_tools: MCPTools | None = None

        logger.debug(f"JiraAgent initialized: storage_path={storage_path}, user_id={user_id}, use_mcp={use_mcp}")

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

    def _build_mcp_command(self) -> tuple[str, dict[str, str], list[str]]:
        """Build the MCP command configuration for the Atlassian server.

        Returns:
            Tuple of (command, environment_dict, included_tools)
        """
        # Get environment variables
        jira_url = getenv("JIRA_URL")
        jira_token = getenv("JIRA_PERSONAL_TOKEN")

        if not jira_url:
            raise ValueError("JIRA_URL environment variable is required for MCP integration")

        if not jira_token:
            raise ValueError("JIRA_PERSONAL_TOKEN environment variable is required for MCP integration")

        # Build environment dictionary for MCP server
        mcp_env = {
            "JIRA_URL": jira_url,
            "JIRA_PERSONAL_TOKEN": jira_token,
            "READ_ONLY_MODE": "true",
            "ENABLED_TOOLS": "jira_get_issue",
        }

        # Define the tools we want to include
        included_tools = ["jira_get_issue"]

        # Build the command
        command = "uvx mcp-atlassian -v"

        logger.debug(f"MCP command: {command}")
        logger.debug(f"MCP environment: {list(mcp_env.keys())}")  # Log keys only, not values
        logger.debug(f"MCP included tools: {included_tools}")

        return command, mcp_env, included_tools

    async def initialize(self) -> None:
        """Initialize the agent with Jira tools (lazy loading)."""
        if self._initialized:
            logger.debug("Jira agent already initialized")
            return

        try:
            logger.info(f"Initializing Jira agent with {'MCP' if self.use_mcp else 'JiraTools'}")

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Create agent storage
            storage = SqliteStorage(
                table_name="jira_agent_sessions",
                db_file=str(self.storage_path),
            )

            logger.debug(f"Creating Jira agent storage at {self.storage_path}")

            # Log required environment variables for Jira and GitHub
            jira_url = getenv("JIRA_URL")
            jira_token = getenv("JIRA_PERSONAL_TOKEN")
            github_token = getenv("GITHUB_ACCESS_TOKEN")

            logger.info(f"JIRA_URL: {'set' if jira_url else 'NOT SET'}")
            logger.info(f"JIRA_PERSONAL_TOKEN: {'set' if jira_token else 'NOT SET'}")
            logger.info(f"GITHUB_ACCESS_TOKEN: {'set' if github_token else 'NOT SET'}")

            # Choose tools based on configuration
            if self.use_mcp:
                # Use MCP Atlassian server
                logger.info("Using MCP Atlassian server")

                # Build MCP command configuration
                mcp_command, mcp_env, included_tools = self._build_mcp_command()

                # Initialize MCP tools with environment variables and specific tools
                self._mcp_tools = MCPTools(
                    command=mcp_command,
                    env=mcp_env,
                    include_tools=included_tools,
                )
                tools = [self._mcp_tools]

                instructions = [
                    "You are a Jira ticket processing agent that extracts key information from tickets "
                    "using MCP Atlassian server.",
                    "When given a Jira ticket ID, fetch the ticket details and extract relevant information.",
                    "Look for GitHub pull request URLs in the ticket description and comments.",
                    "Extract the following information:",
                    "- Ticket key, summary, description, status, priority",
                    "- Components, labels, assignee, reporter",
                    "- Any GitHub PR URLs mentioned in the ticket",
                    "- Creation and update dates",
                    "Return the information in a structured format that can be used for release notes generation.",
                    "Be thorough in extracting PR links from all ticket content.",
                    "Use the available MCP tools to interact with Jira.",
                    "Use jira_get_issue to fetch the ticket details.",
                ]
            else:
                # Use custom Jira tools
                logger.info("Using custom Jira tools")
                # tools = [jira_get_issue, jira_search_issues, jira_add_comment, jira_create_issue]  # type: ignore
                tools = [jira_get_issue, jira_search_issues]

                instructions = [
                    "You are a Jira ticket processing agent that extracts key information from tickets.",
                    "When given a Jira ticket ID, fetch the ticket details and extract relevant information.",
                    "Look for GitHub pull request URLs in the ticket description and comments.",
                    "Extract the following information:",
                    "- Ticket key, summary, description, status, priority",
                    "- Components, labels, assignee, reporter",
                    "- Any GitHub PR URLs mentioned in the ticket",
                    "- Creation and update dates",
                    "Return the information in a structured format that can be used for release notes generation.",
                    "Be thorough in extracting PR links from all ticket content.",
                    "Use the available Jira tools to interact with Jira.",
                    "Use jira_get_issue to fetch the ticket details.",
                ]

            # Create the agent with optional structured output
            agent_kwargs = {
                "name": "Jira Ticket Processor",
                "model": Gemini(id="gemini-2.0-flash"),
                "instructions": instructions,
                "tools": tools,
                "storage": storage,
                "add_datetime_to_instructions": True,
                "add_history_to_messages": True,
                "num_history_runs": 3,
                "markdown": True,
            }

            # Only add response_model if structured output is enabled
            if self.use_structured_output:
                agent_kwargs["response_model"] = JiraIssueData
                agent_kwargs["markdown"] = False

            self._agent = Agent(**agent_kwargs)

            self._initialized = True
            logger.info("Jira agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Jira agent: {e}")
            self._initialized = False
            raise RuntimeError(f"Jira agent initialization failed: {e}") from e

    async def fetch_ticket(self, ticket_id: str, session_id: str | None = None) -> RunResponse:
        """
        Fetch and process a Jira ticket.

        Args:
            ticket_id: Jira ticket ID (e.g., PROJ-123)
            session_id: Optional session ID to use for this request

        Returns:
            RunResponse from the agent
        """
        # Ensure agent is initialized
        if not self._initialized:
            await self.initialize()

        if self._agent is None:
            raise RuntimeError("Jira agent not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.debug(f"Fetching Jira ticket: '{ticket_id}' with session_id={self._session_id}")

        # Create the prompt for the agent
        prompt = f"""
        Please fetch and analyze the Jira ticket {ticket_id}.

        Extract the following information:
        1. Basic ticket details (key, summary, description, status, priority)
        2. Components and labels
        3. Assignee and reporter information
        4. Creation and update dates
        5. Any GitHub pull request URLs mentioned in the ticket description or comments

        Return the information in a structured format that includes all the extracted data.
        """

        try:
            # Get response from agent
            if self.use_mcp and self._mcp_tools:
                # Use MCP tools as context manager
                async with self._mcp_tools:
                    response = await self._agent.arun(
                        prompt, stream=False, session_id=self._session_id, user_id=self.user_id
                    )
            else:
                # Use traditional tools
                response = self._agent.run(prompt, stream=False, session_id=self._session_id, user_id=self.user_id)

            logger.info(f"Jira agent response received for ticket {ticket_id}")

            return response

        except Exception as e:
            logger.error(f"Failed to fetch ticket {ticket_id}: {e}")
            raise RuntimeError(f"Ticket fetch failed: {e}") from e

    def extract_pr_links(self, ticket_id: str) -> list[str]:
        """
        Extract GitHub pull request links from a Jira ticket.

        Args:
            ticket_id: Jira ticket ID

        Returns:
            List of GitHub PR URLs found in the ticket
        """
        # This will be implemented in Stage 3 with actual Jira API integration
        logger.debug(f"Extracting PR links from ticket {ticket_id}")

        # Placeholder - will return actual PR links in Stage 3
        return []

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup if needed
        pass
