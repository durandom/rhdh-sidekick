"""
Release Notes Agent with JIRA and GitHub tools.

This module implements an AI agent that generates release notes from JIRA tickets
and associated GitHub pull requests using the Agno framework.
"""

import uuid
from pathlib import Path

from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.github import GithubTools
from loguru import logger

from ..tools.jira import jira_get_issue, jira_search_issues


class ReleaseNotesAgent:
    """AI-powered release notes agent using Agno framework with JIRA and GitHub tools."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
    ):
        """
        Initialize the release notes agent.

        Args:
            storage_path: Path for agent session storage
            user_id: Optional user ID for session management
        """
        # Default storage path
        if storage_path is None:
            storage_path = Path("tmp/release_notes_agent.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self._agent: Agent | None = None
        self._initialized = False
        self._session_id: str | None = None

        logger.debug(f"ReleaseNotesAgent initialized: storage_path={storage_path}, user_id={user_id}")

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
        """Initialize the agent with JIRA and GitHub tools."""
        if self._initialized:
            logger.debug("Agent already initialized")
            return

        try:
            logger.info("Initializing release notes agent")

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Create agent storage
            storage = SqliteStorage(
                table_name="release_notes_sessions",
                db_file=str(self.storage_path),
            )

            # Initialize tools
            tools = []

            # Add JIRA tools
            tools.extend([jira_get_issue, jira_search_issues])

            # Add GitHub tools - only get_pull_request_tool as requested
            github_tools = GithubTools(
                get_pull_request_with_details=True, get_pull_request=True, get_pull_request_changes=True
            )
            tools.append(github_tools)

            # Create the agent
            self._agent = Agent(
                name="Release Notes Generator",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are a release notes generation assistant.",
                    "Your task is to generate well-formatted release notes from JIRA tickets and GitHub pull requests.",
                    "When given a JIRA ticket ID, use jira_get_issue to fetch the ticket details.",
                    "Extract any GitHub pull request links from the ticket description, comments, or fields.",
                    "For each GitHub PR link found, use get_pull_request to fetch the PR details.",
                    "Generate comprehensive release notes that include:",
                    "- A clear title based on the JIRA ticket summary",
                    "- Key changes and improvements from the PR descriptions",
                    "- Technical details from the changed files when relevant",
                    "- Proper formatting in markdown or text as requested",
                    "Always be thorough but concise in your release notes.",
                    "Focus on user-facing changes and important technical improvements.",
                    "Don't make up details that are not present in the ticket or PR.",
                    "Always fetch the jira ticket first before processing PRs.",
                    "If no Jira ticket is provided, ask for one.",
                ],
                tools=tools,
                storage=storage,
                add_datetime_to_instructions=True,
                add_history_to_messages=True,
                num_history_runs=3,
                markdown=True,
            )

            self._initialized = True
            logger.info("Release notes agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize release notes agent: {e}")
            self._initialized = False
            raise RuntimeError(f"Agent initialization failed: {e}") from e

    def generate_release_notes(
        self, ticket_id: str, session_id: str | None = None, output_format: str = "markdown"
    ) -> RunResponse:
        """
        Generate release notes from a JIRA ticket ID.

        Args:
            ticket_id: JIRA ticket ID (e.g., PROJ-123)
            session_id: Optional session ID to use for this generation
            output_format: Output format (markdown, text)

        Returns:
            Agent response with generated release notes
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

        logger.debug(f"Generating release notes for ticket: '{ticket_id}' with session_id={self._session_id}")

        # Construct the prompt
        prompt = f"""
Generate release notes for JIRA ticket {ticket_id}.

Please follow these steps:
1. Use jira_get_issue to fetch the JIRA ticket details for {ticket_id}
   **Important:** Always fetch the JIRA ticket first before continuing. Without the ticket, you cannot proceed.
2. Extract any GitHub pull request links from the ticket description, comments, or fields
3. For each GitHub PR link found, use get_pull_request to fetch the PR details
4. Generate comprehensive release notes in {output_format} format

The release notes should include:
- A clear title based on the JIRA ticket summary
- Key changes and improvements from the PR descriptions
- Technical details from the changed files when relevant
- Proper formatting in {output_format}

Focus on user-facing changes and important technical improvements.

ATTENTION: Do not make up details that are not present. The first thing you must do is fetch the JIRA ticket.
Use the jira_get_issue tool to get the ticket details before processing any PRs.
If no JIRA ticket is provided, ask for one.
"""

        # Get response from agent
        response = self._agent.run(prompt, stream=False, session_id=self._session_id, user_id=self.user_id)

        return response

    def ask(self, query: str, session_id: str | None = None) -> RunResponse:
        """
        Ask a follow-up question or request modifications to the release notes.

        Args:
            query: Question or modification request
            session_id: Optional session ID to use for this query

        Returns:
            Agent response
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

        logger.debug(f"Processing ask query: '{query}' with session_id={self._session_id}")

        # Get response from agent
        response = self._agent.run(query, stream=False, session_id=self._session_id, user_id=self.user_id)

        return response
