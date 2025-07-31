"""
Generic Jira integration agent for interactive ticket processing.

This module implements an AI agent using the Agno framework that can interact
with Jira in a conversational manner. Supports both JiraTools and MCP Atlassian
server integration with interactive question loops.
"""

from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.tools.mcp import MCPTools
from loguru import logger

from .base import BaseAgentFactory
from .mixins import JiraMixin, StorageMixin, WorkspaceMixin


class JiraAgent(JiraMixin, StorageMixin, WorkspaceMixin, BaseAgentFactory):
    """Factory class for creating Jira-enabled Agno agents with MCP integration."""

    def __init__(
        self,
        storage_path: Path | None = None,
        workspace_dir: Path | None = None,
        memory: Memory | None = None,
    ):
        """
        Initialize the Jira agent factory.

        Args:
            storage_path: Path for agent session storage
            workspace_dir: Path to workspace directory for file operations
            memory: Memory instance for user memory management
        """
        # Default storage path
        if storage_path is None:
            storage_path = self.get_default_storage_path("jira")

        super().__init__(
            storage_path=storage_path,
            workspace_dir=workspace_dir,
            memory=memory,
            read_only_mode=True,  # JiraAgent uses read-only mode
        )

        logger.debug(f"JiraAgent factory initialized: storage_path={storage_path}, workspace_dir={workspace_dir}")

    def get_agent_instructions(self) -> list[str]:
        """Get the instructions for the Jira agent.

        Returns:
            List of instruction strings for the agent
        """
        # Use the new prompt template system
        jira_url = getenv("JIRA_URL", "your JIRA instance")
        return self.get_agent_instructions_from_template(jira_instance=jira_url)

    def create_agent(self, mcp_tools: MCPTools) -> Agent:
        """Create and return a configured Agno Agent with Jira capabilities.

        Args:
            mcp_tools: Configured MCP tools instance

        Returns:
            Configured Agno Agent instance
        """
        # Log required environment variables
        self.log_jira_env_status()

        # Create storage
        storage = self.create_storage("jira_agent_sessions")

        # Get instructions
        instructions = self.get_agent_instructions()

        # Create file tools for workspace operations
        file_tools = self.create_file_tools()

        # Create the agent
        agent = Agent(
            name="Jira Assistant",
            model=Gemini(id="gemini-2.5-flash"),
            instructions=instructions,
            tools=[mcp_tools, file_tools],
            storage=storage,
            memory=self.memory,
            enable_agentic_memory=bool(self.memory),
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_runs=3,
            markdown=True,
        )

        logger.info("Jira agent created successfully")
        return agent

    def get_required_env_vars(self) -> list[str]:
        """Return list of required environment variables."""
        return super().get_required_env_vars()  # From JiraMixin

    async def setup_context(self) -> MCPTools:
        """Setup async context - create and start MCP tools."""
        return await self.setup_mcp_context()

    async def cleanup_context(self, context: MCPTools) -> None:
        """Cleanup async context - stop MCP tools."""
        await self.cleanup_mcp_context(context)
