"""
Generic GitHub integration agent for interactive repository processing.

This module implements an AI agent using the Agno framework that can interact
with GitHub repositories in a conversational manner. Uses agno.tools.github
for GitHub API access with interactive question loops.
"""

from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.file import FileTools
from agno.tools.github import GithubTools
from loguru import logger

from .base import BaseAgentFactory


class GitHubAgent(BaseAgentFactory):
    """Factory class for creating GitHub-enabled Agno agents."""

    def __init__(
        self,
        storage_path: Path | None = None,
        repository: str | None = None,
        workspace_dir: Path | None = None,
        memory: Memory | None = None,
    ):
        """
        Initialize the GitHub agent factory.

        Args:
            storage_path: Path for agent session storage
            repository: Default repository to work with (format: "owner/repo")
            workspace_dir: Path to workspace directory for file operations
            memory: Memory instance for user memory management
        """
        # Default storage path
        if storage_path is None:
            storage_path = self.get_default_storage_path("github")

        self.workspace_dir = workspace_dir or Path("./workspace")

        super().__init__(storage_path=storage_path, memory=memory, repository=repository)
        self.repository = repository

        logger.debug(
            f"GitHubAgent factory initialized: storage_path={storage_path}, "
            f"repository={repository}, workspace_dir={self.workspace_dir}"
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

        # Create GitHub tools with all capabilities enabled
        github_tools = GithubTools(
            access_token=github_token,
            search_repositories=True,
            list_repositories=True,
            get_repository=True,
            get_pull_request=True,
            get_pull_request_changes=True,
            get_pull_request_comments=True,
            list_branches=True,
            get_pull_request_count=True,
            get_pull_requests=True,
            get_pull_request_with_details=True,
            get_repository_with_stats=True,
            list_issues=True,
            get_issue=True,
            get_file_content=True,
            get_directory_content=True,
            get_branch_content=True,
            search_code=True,
            search_issues_and_prs=True,
        )

        logger.debug("GitHub tools created successfully")
        return github_tools

    def get_agent_instructions(self) -> list[str]:
        """Get the instructions for the GitHub agent.

        Returns:
            List of instruction strings for the agent
        """
        # Use the new prompt template system
        instructions = self.get_agent_instructions_from_template(default_repository=self.repository or "")

        # Add repository-specific instructions if repository is set
        if self.repository:
            instructions.append(f"You are primarily working with the repository: {self.repository}")
            instructions.append(
                "When users ask about 'this repo' or don't specify a repository, use this default repository."
            )

        return instructions

    def create_storage(self) -> SqliteStorage:
        """Create and return configured storage for the agent.

        Returns:
            Configured SqliteStorage instance
        """
        # Create storage directory if needed
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        storage = SqliteStorage(
            table_name="github_agent_sessions",
            db_file=str(self.storage_path),
        )

        logger.debug(f"Created GitHub agent storage at {self.storage_path}")
        return storage

    def create_agent(self, github_tools: GithubTools) -> Agent:
        """Create and return a configured Agno Agent with GitHub capabilities.

        Args:
            github_tools: Configured GitHub tools instance

        Returns:
            Configured Agno Agent instance
        """
        # Log required environment variables
        github_token = getenv("GITHUB_ACCESS_TOKEN")

        logger.info(f"GITHUB_ACCESS_TOKEN: {'set' if github_token else 'NOT SET'}")

        # Create storage
        storage = self.create_storage()

        # Get instructions
        instructions = self.get_agent_instructions()

        # Create file tools for workspace operations
        file_tools = FileTools(base_dir=self.workspace_dir)

        # Create the agent
        agent = Agent(
            name="GitHub Assistant",
            model=Gemini(id="gemini-2.5-flash"),
            instructions=instructions,
            tools=[github_tools, file_tools],
            storage=storage,
            memory=self.memory,
            enable_agentic_memory=bool(self.memory),
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_runs=3,
            markdown=True,
        )

        logger.info("GitHub agent created successfully")
        return agent

    def get_required_env_vars(self) -> list[str]:
        """Return list of required environment variables."""
        return ["GITHUB_ACCESS_TOKEN"]

    async def setup_context(self) -> GithubTools:
        """Setup async context - create GitHub tools."""
        return self.create_github_tools()

    async def cleanup_context(self, context: GithubTools) -> None:
        """Cleanup async context - nothing to cleanup for GitHub tools."""
        pass

    def get_extra_info(self) -> list[str]:
        """Get extra information to display when starting the agent."""
        info = []
        if self.repository:
            info.append(f"[dim]Default repository: {self.repository}[/dim]")
        return info
