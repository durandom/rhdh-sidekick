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
from agno.storage.sqlite import SqliteStorage
from agno.tools.file import FileTools
from agno.tools.knowledge import KnowledgeTools
from agno.tools.mcp import MCPTools
from agno.tools.reasoning import ReasoningTools
from loguru import logger

from ..knowledge import KnowledgeManager
from .base import BaseAgentFactory


class ReleaseManagerAgent(BaseAgentFactory):
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

        self.workspace_dir = workspace_dir or Path("./workspace")
        self.knowledge_manager = KnowledgeManager(knowledge_path=knowledge_path)
        self._knowledge: Any = None  # Will be loaded during setup_context

        super().__init__(storage_path=storage_path, memory=memory)

        logger.debug(
            f"ReleaseManagerAgent factory initialized: storage_path={storage_path}, workspace_dir={self.workspace_dir}"
        )

    def build_mcp_command(self) -> tuple[str, dict[str, str], list[str]]:
        """Build the MCP command configuration for the Atlassian server.

        Returns:
            Tuple of (command, environment_dict, included_tools)

        Raises:
            ValueError: If required environment variables are missing
        """
        # Get environment variables
        jira_url = getenv("JIRA_URL")
        jira_token = getenv("JIRA_PERSONAL_TOKEN")

        if not jira_url:
            raise ValueError("JIRA_URL environment variable is required for MCP integration")

        if not jira_token:
            raise ValueError("JIRA_PERSONAL_TOKEN environment variable is required for MCP integration")

        # Build environment dictionary for MCP server - same as JiraAgent but with write access
        mcp_env = {
            "JIRA_URL": jira_url,
            "JIRA_PERSONAL_TOKEN": jira_token,
            "READ_ONLY_MODE": "false",  # Release Manager needs write access
            "ENABLED_TOOLS": "jira_get_issue,jira_search",  # Start with basic tools
        }

        # Define the tools we want to include - same as JiraAgent for now
        included_tools = ["jira_get_issue", "jira_search"]

        # Build the command
        command = "uvx mcp-atlassian -v"

        logger.debug(f"MCP command: {command}")
        logger.debug(f"MCP environment: {list(mcp_env.keys())}")  # Log keys only, not values
        logger.debug(f"MCP included tools: {included_tools}")

        return command, mcp_env, included_tools

    def create_mcp_tools(self) -> MCPTools:
        """Create and return configured MCP tools for Jira integration.

        Returns:
            Configured MCPTools instance

        Raises:
            ValueError: If required environment variables are missing
        """
        command, mcp_env, included_tools = self.build_mcp_command()

        return MCPTools(
            command=command,
            env=mcp_env,
            include_tools=included_tools,
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

    def create_storage(self) -> SqliteStorage:
        """Create and return configured storage for the agent.

        Returns:
            Configured SqliteStorage instance
        """
        # Create storage directory if needed
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        storage = SqliteStorage(
            table_name="release_manager_sessions",
            db_file=str(self.storage_path),
        )

        logger.debug(f"Created Release Manager agent storage at {self.storage_path}")
        return storage

    def create_agent(self, context: tuple[MCPTools, Any]) -> Agent:
        """Create and return a configured Agno Agent with Release Manager capabilities.

        Args:
            context: Tuple of (mcp_tools, knowledge) from setup_context

        Returns:
            Configured Agno Agent instance
        """
        mcp_tools, knowledge = context

        # Log required environment variables
        jira_url = getenv("JIRA_URL")
        jira_token = getenv("JIRA_PERSONAL_TOKEN")

        logger.info(f"JIRA_URL: {'set' if jira_url else 'NOT SET'}")
        logger.info(f"JIRA_PERSONAL_TOKEN: {'set' if jira_token else 'NOT SET'}")

        # Create storage
        storage = self.create_storage()

        # Get instructions
        instructions = self.get_agent_instructions()

        # Create file tools for workspace operations
        file_tools = FileTools(base_dir=self.workspace_dir)

        # Create knowledge tools
        knowledge_tools = KnowledgeTools(
            knowledge=knowledge,
            think=True,
            search=True,
            analyze=True,
            add_instructions=True,
            add_few_shot=True,
        )

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
        return ["JIRA_URL", "JIRA_PERSONAL_TOKEN"]

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
        mcp_tools = self.create_mcp_tools()
        await mcp_tools.__aenter__()

        # Load knowledge base
        logger.info("Loading knowledge base for Release Manager agent")
        knowledge = await self.knowledge_manager.aload_knowledge(recreate=False)

        return mcp_tools, knowledge

    async def cleanup_context(self, context: tuple[MCPTools, Any]) -> None:
        """Cleanup async context - stop MCP tools.

        Args:
            context: Tuple of (mcp_tools, knowledge) from setup_context
        """
        if context and isinstance(context, tuple):
            mcp_tools, _ = context
            if mcp_tools:
                try:
                    await mcp_tools.__aexit__(None, None, None)
                except Exception as e:
                    logger.warning(f"Error cleaning up Release Manager MCP tools: {e}")
