"""
Base agent factory interface for creating Agno agents.

This module provides the abstract base class that all agent factories
should implement to ensure consistency across different agent types.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from agno.agent import Agent
from agno.memory.v2.memory import Memory
from loguru import logger

from ..prompts import BasePromptTemplate, get_prompt_registry
from ..prompts.loaders import load_prompt_template


class BaseAgentFactory(ABC):
    """Abstract base factory for creating Agno agents with consistent interfaces."""

    def __init__(self, storage_path: Path | None = None, memory: Memory | None = None, **kwargs):
        """
        Initialize the agent factory.

        Args:
            storage_path: Path for agent session storage
            memory: Memory instance for user memory management
            **kwargs: Additional agent-specific parameters
        """
        self.storage_path = storage_path
        self.memory = memory
        self.kwargs = kwargs
        self._prompt_template: BasePromptTemplate | None = None

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
        return Path("tmp/sidekick.db")

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

    def get_prompt_template_name(self) -> str:
        """
        Get the name of the prompt template for this agent.

        Returns:
            Template name (defaults to agent display name)
        """
        # Default to agent display name with 'agents.' prefix
        return f"agents.{self.get_display_name()}"

    def load_prompt_template(self, template_name: str | None = None) -> BasePromptTemplate:
        """
        Load the prompt template for this agent.

        Args:
            template_name: Optional template name to override default

        Returns:
            BasePromptTemplate instance
        """
        if self._prompt_template is None:
            name = template_name or self.get_prompt_template_name()
            try:
                # Try to get from registry first
                registry = get_prompt_registry()
                self._prompt_template = registry.get(name)
                logger.debug(f"Loaded prompt template '{name}' from registry")
            except KeyError:
                # Fall back to loading from file
                template_path = (
                    Path(__file__).parent.parent / "prompts" / "templates" / f"{name.replace('.', '/')}.yaml"
                )
                if template_path.exists():
                    self._prompt_template = load_prompt_template(template_path)
                    logger.debug(f"Loaded prompt template from file: {template_path}")
                else:
                    logger.warning(f"No prompt template found for '{name}', using legacy instructions")
                    # Create a template from legacy instructions
                    from ..prompts import PromptConfig

                    instructions = self.get_agent_instructions()
                    self._prompt_template = BasePromptTemplate(
                        config=PromptConfig(
                            name=name, description=f"Legacy instructions for {self.get_display_name()}"
                        ),
                        template_content="\n\n".join(instructions),
                    )
        return self._prompt_template

    def get_agent_instructions_from_template(self, **kwargs) -> list[str]:
        """
        Get agent instructions from the prompt template.

        Args:
            **kwargs: Variables to pass to the template

        Returns:
            List of instruction strings
        """
        template = self.load_prompt_template()
        return template.get_instructions_list(**kwargs)
