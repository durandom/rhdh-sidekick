"""
Release Notes Generation Workflow.

This module implements a workflow that orchestrates multiple agents to generate
release notes from Jira tickets and associated GitHub pull requests.

!!!Currently not used.
"""

import uuid
from pathlib import Path
from typing import Any

from agno.utils.pprint import pprint_run_response
from loguru import logger
from rich import print
from rich.panel import Panel
from rich.pretty import Pretty

from ..agents.jira_agent import JiraAgent
from ..tools.jira import parse_json_to_jira_issue


class ReleaseNotesGenerator:
    """Workflow for generating release notes from Jira tickets."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
    ):
        """
        Initialize the release notes generator workflow.

        Args:
            storage_path: Path for workflow session storage
            user_id: Optional user ID for session management
        """
        # Default storage path
        if storage_path is None:
            storage_path = Path("tmp/release_notes_workflow.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self._session_id: str | None = None

        # Initialize agents
        self.jira_agent_factory = JiraAgent(storage_path=storage_path.parent / "jira_agent.db")

        # TODO: Initialize other agents in future stages
        # self.github_agent = GithubAgent(...)
        # self.release_notes_agent = ReleaseNotesAgent(...)

        logger.debug(f"ReleaseNotesGenerator initialized: storage_path={storage_path}, user_id={user_id}")

    def _generate_session_id(self) -> str:
        """Generate a new session ID using UUID."""
        return str(uuid.uuid4())

    def create_session(self, user_id: str | None = None) -> str:
        """
        Create a new session for the workflow.

        Args:
            user_id: Optional user ID to override the instance user_id

        Returns:
            The generated session ID
        """
        if user_id is not None:
            self.user_id = user_id

        self._session_id = self._generate_session_id()

        logger.info(f"Created new workflow session: session_id={self._session_id}, user_id={self.user_id}")
        return self._session_id

    def get_current_session(self) -> str | None:
        """
        Get the current session ID.

        Returns:
            Current session ID or None if no session exists
        """
        return self._session_id

    async def generate_release_notes(
        self,
        ticket_id: str,
        output_format: str = "markdown",
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate release notes from a Jira ticket.

        This workflow:
        1. Fetches ticket details from Jira
        2. Extracts GitHub PR links from the ticket
        3. Fetches PR details for each link
        4. Generates formatted release notes

        Args:
            ticket_id: Jira ticket ID (e.g., PROJ-123)
            output_format: Output format (markdown, text)
            session_id: Optional session ID to use for this workflow

        Returns:
            Dictionary containing the generated release notes and metadata
        """
        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.info(f"Starting release notes generation for ticket {ticket_id}")

        try:
            # Step 1: Fetch Jira ticket details
            logger.debug(f"Step 1: Fetching Jira ticket {ticket_id}")

            # Create MCP tools and agent using the factory pattern
            mcp_tools = self.jira_agent_factory.create_mcp_tools()

            # Use MCP tools as async context manager
            async with mcp_tools:
                # Create the agent within the MCP context
                jira_agent = self.jira_agent_factory.create_agent(mcp_tools)

                # Ask the agent to fetch the ticket details
                jira_response = await jira_agent.arun(
                    f"Get detailed information for Jira ticket {ticket_id}",
                    session_id=self._session_id,
                    user_id=self.user_id,
                )

            # Print response

            # Parse the response content into a JiraIssueData object
            jira_issue = None
            if jira_response.content:
                jira_issue = parse_json_to_jira_issue(jira_response.content)
                if jira_issue:
                    logger.debug(f"Successfully parsed Jira issue: {jira_issue.key}")
                    # use rich to pretty print the Jira issue
                    pretty = Pretty(jira_issue.model_dump())
                    panel = Panel(pretty, title=f"Jira Issue: {jira_issue.key}")
                    print(panel)

                else:
                    logger.warning(f"Failed to parse Jira response as JiraIssueData for ticket {ticket_id}")
                    pprint_run_response(jira_response, markdown=True, show_time=True)
            else:
                logger.warning(f"No content in Jira response for ticket {ticket_id}")
                pprint_run_response(jira_response, markdown=True, show_time=True)

            # TODO: Step 3: Fetch GitHub PR details for each link
            # pr_details = []
            # for pr_url in pr_links:
            #     pr_detail = self.github_agent.fetch_pr(pr_url, session_id=self._session_id)
            #     pr_details.append(pr_detail)

            # TODO: Step 4: Generate release notes using AI
            # release_notes = self.release_notes_agent.generate_notes(
            #     jira_issue=jira_issue,
            #     pr_details=pr_details,
            #     output_format=output_format,
            #     session_id=self._session_id,
            # )

            # For now, return placeholder data
            result = {
                "ticket_id": ticket_id,
                "session_id": self._session_id,
                "jira_issue": jira_issue.model_dump() if jira_issue else None,
                "pr_links": jira_issue.pull_requests if jira_issue else [],
                "pr_details": [],  # Will be populated in Stage 4
                "release_notes": f"[Placeholder] Release notes for {ticket_id} will be generated here",
                "output_format": output_format,
                "status": "completed",
                "metadata": {
                    "workflow_version": "stage_2",
                    "agents_used": ["jira_agent"],
                    "timestamp": str(uuid.uuid4()),  # Placeholder for actual timestamp
                },
            }

            logger.info(f"Release notes generation completed for ticket {ticket_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to generate release notes for ticket {ticket_id}: {e}")
            raise RuntimeError(f"Release notes generation failed: {e}") from e

    def get_workflow_status(self, session_id: str | None = None) -> dict[str, Any]:
        """
        Get the current status of the workflow.

        Args:
            session_id: Optional session ID to check

        Returns:
            Dictionary containing workflow status information
        """
        current_session = session_id or self._session_id

        if current_session is None:
            return {
                "status": "no_session",
                "message": "No active session",
                "session_id": None,
            }

        return {
            "status": "active",
            "session_id": current_session,
            "user_id": self.user_id,
            "agents": {
                "jira_agent_factory": {
                    "storage_path": str(self.jira_agent_factory.storage_path),
                },
                # TODO: Add other agents in future stages
            },
        }
