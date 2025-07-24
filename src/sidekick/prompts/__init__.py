"""
Prompt template management for Sidekick agents.

This module provides a LangChain-based prompt template system that allows
for easy customization and management of agent instructions.
"""

from .base import BasePromptTemplate, PromptConfig
from .loaders import PromptLoader, YAMLPromptLoader
from .registry import PromptRegistry, get_prompt_registry

__all__ = [
    "BasePromptTemplate",
    "PromptConfig",
    "PromptLoader",
    "YAMLPromptLoader",
    "PromptRegistry",
    "get_prompt_registry",
]
