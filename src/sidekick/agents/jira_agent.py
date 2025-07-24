"""
Generic Jira integration agent for interactive ticket processing.

This module implements an AI agent using the Agno framework that can interact
with Jira in a conversational manner. Supports both JiraTools and MCP Atlassian
server integration with interactive question loops.
"""

from os import getenv
from pathlib import Path

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.mcp import MCPTools
from loguru import logger


class JiraAgent:
    """Factory class for creating Jira-enabled Agno agents with MCP integration."""

    def __init__(
        self,
        storage_path: Path | None = None,
    ):
        """
        Initialize the Jira agent factory.

        Args:
            storage_path: Path for agent session storage
        """
        # Default storage path
        if storage_path is None:
            storage_path = Path("tmp/jira_agent.db")

        self.storage_path = storage_path

        logger.debug(f"JiraAgent factory initialized: storage_path={storage_path}")

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

        # Build environment dictionary for MCP server
        mcp_env = {
            "JIRA_URL": jira_url,
            "JIRA_PERSONAL_TOKEN": jira_token,
            "READ_ONLY_MODE": "true",
            "ENABLED_TOOLS": "jira_get_issue,jira_search",
        }

        # Define the tools we want to include
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
        """Get the instructions for the Jira agent.

        Returns:
            List of instruction strings for the agent
        """
        return [
            "You are a helpful Jira assistant that can interact with Jira tickets and issues using MCP "
            "Atlassian server.",
            "You can help with various Jira-related tasks including:",
            "- Fetching ticket details and information",
            "- Searching for tickets based on criteria",
            "- Analyzing ticket content and relationships",
            "- Extracting specific information from tickets",
            "- Answering questions about ticket status, progress, and details",
            "- Finding GitHub PR links or other references in tickets",
            "When users ask questions about tickets, use the available Jira tools to gather the necessary information.",
            "Be conversational and helpful in your responses.",
            "Use jira_get_issue to fetch specific ticket details.",
            "Use jira_search to find tickets based on criteria.",
            "Always provide clear, structured responses based on the ticket data you retrieve.",
        ]

    def create_storage(self) -> SqliteStorage:
        """Create and return configured storage for the agent.

        Returns:
            Configured SqliteStorage instance
        """
        # Create storage directory if needed
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        storage = SqliteStorage(
            table_name="jira_agent_sessions",
            db_file=str(self.storage_path),
        )

        logger.debug(f"Created Jira agent storage at {self.storage_path}")
        return storage

    def create_agent(self, mcp_tools: MCPTools) -> Agent:
        """Create and return a configured Agno Agent with Jira capabilities.

        Args:
            mcp_tools: Configured MCP tools instance

        Returns:
            Configured Agno Agent instance
        """
        # Log required environment variables for Jira and GitHub
        jira_url = getenv("JIRA_URL")
        jira_token = getenv("JIRA_PERSONAL_TOKEN")
        github_token = getenv("GITHUB_ACCESS_TOKEN")

        logger.info(f"JIRA_URL: {'set' if jira_url else 'NOT SET'}")
        logger.info(f"JIRA_PERSONAL_TOKEN: {'set' if jira_token else 'NOT SET'}")
        logger.info(f"GITHUB_ACCESS_TOKEN: {'set' if github_token else 'NOT SET'}")

        # Create storage
        storage = self.create_storage()

        # Get instructions
        instructions = self.get_agent_instructions()

        # Create the agent
        agent = Agent(
            name="Jira Assistant",
            model=Gemini(id="gemini-2.5-flash"),
            instructions=instructions,
            tools=[mcp_tools],
            storage=storage,
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_runs=3,
            markdown=True,
        )

        logger.info("Jira agent created successfully")
        return agent
