"""
RHDH Release Manager agent for coordinating release processes.

This module implements an AI agent using the Agno framework that can coordinate
release management activities for Red Hat Developer Hub (RHDH), including:
- Release planning and scheduling
- Feature tracking and coordination
- Test plan management
- Documentation coordination
- Release readiness assessment
"""

from os import getenv
from pathlib import Path
from typing import Any

from agno.agent import Agent
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.tools.mcp import MCPTools
from agno.tools.reasoning import ReasoningTools
from loguru import logger

from .base import BaseAgentFactory
from .mixins import JiraMixin, KnowledgeMixin, StorageMixin, WorkspaceMixin


class ReleaseManagerAgent(JiraMixin, KnowledgeMixin, StorageMixin, WorkspaceMixin, BaseAgentFactory):
    """Factory class for creating RHDH Release Manager agents with knowledge and Jira integration."""

    def __init__(
        self,
        knowledge_path: Path | None = None,
        storage_path: Path | None = None,
        workspace_dir: Path | None = None,
        memory: Memory | None = None,
    ):
        """
        Initialize the Release Manager agent factory.

        Args:
            knowledge_path: Path to knowledge documents directory
            storage_path: Path for agent session storage
            workspace_dir: Path to workspace directory for file operations
            memory: Memory instance for user memory management
        """
        # Default storage path
        if storage_path is None:
            storage_path = self.get_default_storage_path("release_manager")

        super().__init__(
            storage_path=storage_path,
            workspace_dir=workspace_dir,
            knowledge_path=knowledge_path,
            memory=memory,
            read_only_mode=False,  # Release Manager needs write access
        )

        logger.debug(
            f"ReleaseManagerAgent factory initialized: storage_path={storage_path}, workspace_dir={self.workspace_dir}"
        )

    def get_agent_instructions(self) -> list[str]:
        """Get the instructions for the Release Manager agent.

        Returns:
            List of instruction strings for the agent
        """
        # Use the new prompt template system
        jira_url = getenv("JIRA_URL", "your JIRA instance")
        return self.get_agent_instructions_from_template(
            jira_instance=jira_url,
            knowledge_base_name="RHDH Release Manager documentation",
        )

    def create_agent(self, context: tuple[MCPTools, Any]) -> Agent:
        """Create and return a configured Agno Agent with Release Manager capabilities.

        Args:
            context: Tuple of (mcp_tools, knowledge) from setup_context

        Returns:
            Configured Agno Agent instance
        """
        mcp_tools, knowledge = context

        # Log required environment variables
        self.log_jira_env_status()

        # Create storage
        storage = self.create_storage("release_manager_sessions")

        # Get instructions
        instructions = self.get_agent_instructions()

        # Create file tools for workspace operations
        file_tools = self.create_file_tools()

        # Create knowledge tools
        knowledge_tools = self.create_knowledge_tools(knowledge)

        # Create the agent
        agent = Agent(
            name="RHDH Release Manager",
            model=Gemini(id="gemini-2.5-flash"),
            instructions=instructions,
            tools=[mcp_tools, file_tools, knowledge_tools, ReasoningTools(add_instructions=True)],
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

        logger.info("Release Manager agent created successfully")
        return agent

    def get_required_env_vars(self) -> list[str]:
        """Return list of required environment variables."""
        return super().get_required_env_vars()  # From JiraMixin

    def get_display_name(self) -> str:
        """Get display name for the agent."""
        return "Release Manager"

    def get_prompt_template_name(self) -> str:
        """Get the name of the prompt template for this agent."""
        return "agents.release_manager"

    async def setup_context(self) -> tuple[MCPTools, Any]:
        """Setup async context - create MCP tools and load knowledge base.

        Returns:
            Tuple of (mcp_tools, knowledge)
        """
        logger.info("Setting up Release Manager context")

        # Create and start MCP tools
        mcp_tools = await self.setup_mcp_context()

        # Load knowledge base
        knowledge = await self.load_knowledge(recreate=False)

        return mcp_tools, knowledge

    async def cleanup_context(self, context: tuple[MCPTools, Any]) -> None:
        """Cleanup async context - stop MCP tools.

        Args:
            context: Tuple of (mcp_tools, knowledge) from setup_context
        """
        if context and isinstance(context, tuple):
            mcp_tools, _ = context
            await self.cleanup_mcp_context(mcp_tools)
