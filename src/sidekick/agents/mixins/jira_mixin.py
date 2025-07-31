"""
JIRA MCP integration mixin for agents.

Provides common functionality for MCP Atlassian server integration, including
command building, environment setup, and tool lifecycle management.
"""

from os import getenv

from agno.tools.mcp import MCPTools
from loguru import logger


class JiraMixin:
    """Mixin for JIRA MCP integration functionality."""

    def __init__(self, *args, read_only_mode: bool = True, **kwargs):
        """Initialize JIRA mixin.

        Args:
            read_only_mode: Whether to use read-only mode for JIRA access
            *args: Passed to super().__init__()
            **kwargs: Passed to super().__init__()
        """
        super().__init__(*args, **kwargs)
        self.read_only_mode = read_only_mode
        logger.debug(f"JiraMixin initialized: read_only_mode={read_only_mode}")

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
            "READ_ONLY_MODE": "true" if self.read_only_mode else "false",
            "ENABLED_TOOLS": "jira_get_issue,jira_search",
        }

        # Define the tools we want to include
        included_tools = ["jira_get_issue", "jira_search"]

        # Build the command
        command = "uvx mcp-atlassian -v"

        logger.debug(f"MCP command: {command}")
        logger.debug(f"MCP environment: {list(mcp_env.keys())}")  # Log keys only, not values
        logger.debug(f"MCP included tools: {included_tools}")
        logger.debug(f"MCP read-only mode: {self.read_only_mode}")

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

    def get_required_env_vars(self) -> list[str]:
        """Return list of required environment variables for JIRA integration.

        Returns:
            List of required environment variable names
        """
        return ["JIRA_URL", "JIRA_PERSONAL_TOKEN"]

    def log_jira_env_status(self) -> None:
        """Log the status of required JIRA environment variables."""
        jira_url = getenv("JIRA_URL")
        jira_token = getenv("JIRA_PERSONAL_TOKEN")
        github_token = getenv("GITHUB_ACCESS_TOKEN")

        logger.info(f"JIRA_URL: {'set' if jira_url else 'NOT SET'}")
        logger.info(f"JIRA_PERSONAL_TOKEN: {'set' if jira_token else 'NOT SET'}")
        logger.info(f"GITHUB_ACCESS_TOKEN: {'set' if github_token else 'NOT SET'}")

    async def setup_mcp_context(self) -> MCPTools:
        """Setup async context - create and start MCP tools.

        Returns:
            Started MCPTools instance
        """
        mcp_tools = self.create_mcp_tools()
        await mcp_tools.__aenter__()
        return mcp_tools

    async def cleanup_mcp_context(self, mcp_tools: MCPTools) -> None:
        """Cleanup async context - stop MCP tools.

        Args:
            mcp_tools: MCPTools instance to cleanup
        """
        if mcp_tools:
            try:
                await mcp_tools.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error cleaning up MCP tools: {e}")
