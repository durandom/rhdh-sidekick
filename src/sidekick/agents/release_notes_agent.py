"""
Release Notes Agent with JIRA MCP and GitHub tools.

This module implements an AI agent factory that generates release notes from JIRA tickets
and associated GitHub pull requests using the Agno framework with MCP integration.
"""

from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.tools.github import GithubTools
from loguru import logger

from ..tools.jira import JiraTools
from .base import BaseAgentFactory
from .mixins import StorageMixin, WorkspaceMixin


class ReleaseNotesAgent(StorageMixin, WorkspaceMixin, BaseAgentFactory):
    """Factory class for creating release notes agents with local JIRA tools and GitHub tools."""

    def __init__(
        self,
        storage_path: Path | None = None,
        workspace_dir: Path | None = None,
        memory: Memory | None = None,
    ):
        """
        Initialize the release notes agent factory.

        Args:
            storage_path: Path for agent session storage
            workspace_dir: Path to workspace directory for file operations
            memory: Memory instance for user memory management
        """
        # Default storage path
        if storage_path is None:
            storage_path = self.get_default_storage_path("release_notes")

        super().__init__(
            storage_path=storage_path,
            workspace_dir=workspace_dir,
            memory=memory,
        )

        logger.debug(
            f"ReleaseNotesAgent factory initialized: storage_path={storage_path}, workspace_dir={workspace_dir}"
        )

    def create_github_tools(self) -> GithubTools:
        """Create and return configured GitHub tools.

        Returns:
            Configured GithubTools instance

        Raises:
            ValueError: If required environment variables are missing
        """
        # Get environment variables
        github_token = getenv("GITHUB_ACCESS_TOKEN")

        if not github_token:
            raise ValueError("GITHUB_ACCESS_TOKEN environment variable is required for GitHub integration")

        # Create GitHub tools with PR-focused capabilities
        github_tools = GithubTools(
            access_token=github_token,
            get_pull_request=True,
            get_pull_request_with_details=True,
            get_pull_request_changes=True,
            get_pull_request_comments=True,
            get_repository=True,
            search_repositories=True,
        )

        logger.debug("GitHub tools created successfully for release notes")
        return github_tools

    def create_jira_tools(self) -> JiraTools:
        """Create and return configured local JIRA tools.

        Returns:
            Configured JiraTools instance with only get_issue tool enabled

        Raises:
            ValueError: If required environment variables are missing
        """
        # Only enable get_issue tool for release notes generation
        jira_tools = JiraTools(
            get_issue=True,
            search_issues=False,
            add_comment=False,
            create_issue=False,
        )
        logger.debug("Local JIRA tools created successfully for release notes (get_issue only)")
        return jira_tools

    def get_agent_instructions(self) -> list[str]:
        """Get the instructions for the release notes agent.

        Returns:
            List of instruction strings for the agent
        """
        # Use the new prompt template system
        jira_url = getenv("JIRA_URL", "your JIRA instance")
        return self.get_agent_instructions_from_template(jira_instance=jira_url)

    def create_agent(self, context=None) -> Agent:
        """Create and return a configured Agno Agent with release notes capabilities.

        Args:
            context: Not used for this agent (no MCP tools needed)

        Returns:
            Configured Agno Agent instance
        """
        # Create storage
        storage = self.create_storage("release_notes_agent_sessions")

        # Get instructions
        instructions = self.get_agent_instructions()

        # Create file tools for workspace operations
        file_tools = self.create_file_tools()

        # Create GitHub tools
        github_tools = self.create_github_tools()

        # Create local JIRA tools
        jira_tools = self.create_jira_tools()

        # Create the agent
        agent = Agent(
            name="Release Notes Generator",
            model=Gemini(id="gemini-2.5-flash"),
            instructions=instructions,
            tools=[jira_tools, github_tools, file_tools],
            storage=storage,
            memory=self.memory,
            enable_agentic_memory=True,
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_runs=3,
            markdown=True,
        )

        logger.info("Release notes agent created successfully")
        return agent

    def get_required_env_vars(self) -> list[str]:
        """Return list of required environment variables."""
        return ["JIRA_URL", "JIRA_PERSONAL_TOKEN", "GITHUB_ACCESS_TOKEN"]

    async def setup_context(self) -> None:
        """Setup async context - no context needed for local tools."""
        return None

    async def cleanup_context(self, context) -> None:
        """Cleanup async context - no cleanup needed for local tools."""
        pass

    def get_display_name(self) -> str:
        """Get display name for the agent."""
        return "Release Notes Generator"

    def get_prompt_template_name(self) -> str:
        """Get the name of the prompt template for this agent."""
        return "agents.release_notes"

    def get_extra_info(self) -> list[str]:
        """Get extra information to display when starting the agent."""
        return [
            "[dim]This agent generates release notes from JIRA tickets and GitHub PRs[/dim]",
            "[dim]Required: JIRA_URL, JIRA_PERSONAL_TOKEN, GITHUB_ACCESS_TOKEN[/dim]",
        ]
