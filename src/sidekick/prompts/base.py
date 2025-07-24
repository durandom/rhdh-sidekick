"""
Base classes for prompt template management.

This module provides the foundation for LangChain-based prompt templates
that can be used across different agents in the Sidekick application.
"""

from pathlib import Path
from typing import Any

from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, ConfigDict, Field


class PromptConfig(BaseModel):
    """Configuration for a prompt template."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Name of the prompt template")
    version: str = Field(default="1.0", description="Version of the prompt template")
    description: str = Field(default="", description="Description of the prompt")
    variables: dict[str, Any] = Field(default_factory=dict, description="Default variables for the template")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BasePromptTemplate:
    """
    Base class for managing prompt templates with support for file-based loading,
    composition, and variable substitution.
    """

    def __init__(
        self,
        config: PromptConfig,
        template_content: str | None = None,
        template_path: Path | None = None,
    ):
        """
        Initialize a BasePromptTemplate.

        Args:
            config: Configuration for the prompt template
            template_content: Direct template content (if not loading from file)
            template_path: Path to the template file
        """
        self.config = config
        self.template_path = template_path
        self._template_content = template_content
        self._prompt_template: PromptTemplate | None = None

    @property
    def template_content(self) -> str:
        """Get the template content, loading from file if necessary."""
        if self._template_content is None and self.template_path:
            self._template_content = self.template_path.read_text()
        return self._template_content or ""

    def get_prompt_template(self, **kwargs) -> PromptTemplate:
        """
        Get the LangChain PromptTemplate instance.

        Args:
            **kwargs: Additional arguments to pass to PromptTemplate constructor

        Returns:
            LangChain PromptTemplate instance
        """
        if self._prompt_template is None:
            # Extract variable names from the template
            template = PromptTemplate.from_template(
                template=self.template_content,
                **kwargs,
            )
            self._prompt_template = template
        return self._prompt_template

    def format(self, **kwargs) -> str:
        """
        Format the prompt template with the given variables.

        Args:
            **kwargs: Variables to substitute in the template

        Returns:
            Formatted prompt string
        """
        # Merge default variables with provided ones
        variables = {**self.config.variables, **kwargs}
        prompt = self.get_prompt_template()
        return str(prompt.format(**variables))

    def get_instructions_list(self, **kwargs) -> list[str]:
        """
        Get formatted instructions as a list of strings.

        This is useful for agents that expect instructions as a list.

        Args:
            **kwargs: Variables to substitute in the template

        Returns:
            List of instruction strings
        """
        formatted = self.format(**kwargs)
        # Split by double newlines to separate instruction blocks
        instructions = [instruction.strip() for instruction in formatted.split("\n\n") if instruction.strip()]
        return instructions

    def partial(self, **kwargs) -> "BasePromptTemplate":
        """
        Create a new template with some variables pre-filled.

        Args:
            **kwargs: Variables to pre-fill

        Returns:
            New BasePromptTemplate instance with partial variables
        """
        new_config = self.config.model_copy()
        new_config.variables.update(kwargs)
        return BasePromptTemplate(
            config=new_config,
            template_content=self._template_content,
            template_path=self.template_path,
        )

    def merge_with(self, other: "BasePromptTemplate") -> "BasePromptTemplate":
        """
        Merge this template with another template.

        Args:
            other: Another BasePromptTemplate to merge with

        Returns:
            New BasePromptTemplate with merged content
        """
        # Merge configurations
        merged_config = PromptConfig(
            name=f"{self.config.name}_merged_{other.config.name}",
            version="merged",
            description=f"Merged: {self.config.description} + {other.config.description}",
            variables={**self.config.variables, **other.config.variables},
            metadata={**self.config.metadata, **other.config.metadata},
        )

        # Merge template content
        merged_content = f"{self.template_content}\n\n{other.template_content}"

        return BasePromptTemplate(
            config=merged_config,
            template_content=merged_content,
        )

    def __repr__(self) -> str:
        """String representation of the prompt template."""
        return (
            f"BasePromptTemplate(name='{self.config.name}', "
            f"version='{self.config.version}', "
            f"variables={list(self.config.variables.keys())})"
        )
