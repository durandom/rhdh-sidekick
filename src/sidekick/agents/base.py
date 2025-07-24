"""
Base agent factory interface for creating Agno agents.

This module provides the abstract base class that all agent factories
should implement to ensure consistency across different agent types.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from agno.agent import Agent
from loguru import logger


class BaseAgentFactory(ABC):
    """Abstract base factory for creating Agno agents with consistent interfaces."""

    def __init__(self, storage_path: Path | None = None, **kwargs):
        """
        Initialize the agent factory.

        Args:
            storage_path: Path for agent session storage
            **kwargs: Additional agent-specific parameters
        """
        self.storage_path = storage_path
        self.kwargs = kwargs

    @abstractmethod
    def create_agent(self, *args, **kwargs) -> Agent:
        """
        Create and return a configured Agno Agent.

        Args:
            *args: Positional arguments for agent creation
            **kwargs: Keyword arguments for agent creation

        Returns:
            Configured Agent instance
        """
        pass

    @abstractmethod
    def get_agent_instructions(self) -> list[str]:
        """
        Get the instructions for the agent.

        Returns:
            List of instruction strings
        """
        pass

    @abstractmethod
    def get_required_env_vars(self) -> list[str]:
        """
        Return list of required environment variables.

        Returns:
            List of environment variable names
        """
        pass

    @abstractmethod
    async def setup_context(self) -> Any:
        """
        Setup any async context needed for the agent (e.g., MCP tools).

        Returns:
            Context object(s) needed for agent operation
        """
        pass

    @abstractmethod
    async def cleanup_context(self, context: Any) -> None:
        """
        Cleanup async context.

        Args:
            context: Context object(s) to cleanup
        """
        pass

    def get_default_storage_path(self, agent_name: str) -> Path:
        """
        Get default storage path for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Default storage path
        """
        return Path(f"tmp/{agent_name}_agent.db")

    def get_display_name(self) -> str:
        """
        Get display name for the agent.

        Returns:
            Display name for console output
        """
        # Default implementation - can be overridden
        return self.__class__.__name__.replace("Agent", "").lower()

    def get_extra_info(self) -> list[str]:
        """
        Get extra information to display when starting the agent.

        Returns:
            List of extra info strings to display
        """
        # Default implementation - can be overridden
        return []

    async def initialize_agent(self) -> Agent:
        """
        Initialize and return the agent using the standard pattern.

        This method sets up context, creates the agent, and handles cleanup
        appropriately. Override this method for custom initialization patterns.

        Returns:
            Initialized Agent instance
        """
        logger.info(f"Initializing {self.get_display_name()} agent")

        # Check if agent is already initialized (for agents that manage their own state)
        if hasattr(self, "_agent") and self._agent is not None:
            return self._agent

        # Setup context (e.g., load knowledge, create MCP tools)
        context = await self.setup_context()

        # Create the agent with the context
        try:
            agent = self.create_agent(context)
            # Store context for later cleanup if needed
            self._context = context
            return agent
        except Exception:
            # Cleanup on failure
            await self.cleanup_context(context)
            raise

    async def cleanup(self) -> None:
        """
        Cleanup any resources. Called when agent session ends.
        """
        if hasattr(self, "_context"):
            await self.cleanup_context(self._context)
            delattr(self, "_context")
