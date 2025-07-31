"""Base class for research agents."""

from abc import ABC, abstractmethod
from typing import Any

from agno.agent import Agent
from agno.models.anthropic import Claude
from loguru import logger
from pydantic import BaseModel


class BaseResearchAgent(ABC):
    """Base class for all research agents."""

    def __init__(
        self,
        name: str,
        instructions: str,
        model_id: str = "claude-3-5-sonnet-20241022",
        tools: list | None = None,
    ):
        """Initialize a research agent.

        Args:
            name: Agent name
            instructions: Agent instructions/system prompt
            model_id: Claude model ID to use
            tools: Optional list of tools for the agent
        """
        self.name = name
        self.instructions = instructions
        self.model_id = model_id
        self.tools = tools or []

        # Create the Agno agent
        self.agent = Agent(
            name=name,
            model=Claude(id=model_id),
            instructions=instructions,
            tools=tools,
        )

        logger.debug(f"Initialized {name} agent with model {model_id}")

    @abstractmethod
    async def process(self, input_data: BaseModel) -> BaseModel:
        """Process input and return structured output.

        Args:
            input_data: Structured input data

        Returns:
            Structured output data
        """
        pass

    async def _run_agent(self, messages: list) -> dict[str, Any]:
        """Run the agent with given messages.

        Args:
            messages: List of messages for the agent

        Returns:
            Agent response
        """
        try:
            response = await self.agent.arun(messages=messages)
            return response
        except Exception as e:
            logger.error(f"Error running {self.name} agent: {e}")
            raise

    def _create_message(self, content: str, role: str = "user") -> dict[str, str]:
        """Create a message for the agent.

        Args:
            content: Message content
            role: Message role (user/assistant)

        Returns:
            Message dict
        """
        return {"role": role, "content": content}
