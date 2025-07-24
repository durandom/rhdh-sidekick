"""
Tests for the prompt template system.
"""

import pytest

from sidekick.agents.github_agent import GitHubAgent
from sidekick.agents.jira_agent import JiraAgent
from sidekick.agents.search_agent import SearchAgent
from sidekick.prompts import BasePromptTemplate, PromptConfig, get_prompt_registry


class TestPromptTemplates:
    """Test prompt template functionality."""

    def test_base_prompt_template(self):
        """Test basic prompt template creation and formatting."""
        config = PromptConfig(name="test_template", variables={"name": "World", "greeting": "Hello"})

        template = BasePromptTemplate(config=config, template_content="{greeting}, {name}!")

        # Test basic formatting
        result = template.format()
        assert result == "Hello, World!"

        # Test with override
        result = template.format(name="Python")
        assert result == "Hello, Python!"

    def test_prompt_registry(self):
        """Test prompt registry functionality."""
        registry = get_prompt_registry()

        # Check that agent templates are registered
        templates = registry.list_templates()
        assert "agents.search" in templates
        assert "agents.jira" in templates
        assert "agents.github" in templates

    def test_search_agent_prompts(self):
        """Test SearchAgent uses prompt templates correctly."""
        agent = SearchAgent()
        instructions = agent.get_agent_instructions()

        # Verify it returns a list of instructions
        assert isinstance(instructions, list)
        assert len(instructions) > 0

        # Check for key content from the template
        full_text = "\n".join(instructions)
        assert "CRITICAL KNOWLEDGE BASE SEARCH WORKFLOW:" in full_text
        assert "Think → Search → Analyze" in full_text

    def test_jira_agent_prompts(self):
        """Test JiraAgent uses prompt templates correctly."""
        agent = JiraAgent()
        instructions = agent.get_agent_instructions()

        # Verify it returns a list of instructions
        assert isinstance(instructions, list)
        assert len(instructions) > 0

        # Check for key content from the template
        full_text = "\n".join(instructions)
        assert "Jira assistant" in full_text
        assert "MCP Atlassian server" in full_text

    def test_github_agent_prompts(self):
        """Test GitHubAgent uses prompt templates correctly."""
        # Test without repository
        agent = GitHubAgent()
        instructions = agent.get_agent_instructions()

        assert isinstance(instructions, list)
        assert len(instructions) > 0

        full_text = "\n".join(instructions)
        assert "GitHub assistant" in full_text
        assert "GitHub API" in full_text

        # Test with repository
        agent_with_repo = GitHubAgent(repository="owner/repo")
        instructions_with_repo = agent_with_repo.get_agent_instructions()

        full_text_with_repo = "\n".join(instructions_with_repo)
        assert "owner/repo" in full_text_with_repo
        assert "this repo" in full_text_with_repo

    def test_template_composition(self):
        """Test template composition with includes."""
        registry = get_prompt_registry()

        # Load a template that includes shared instructions
        template = registry.get("agents.search")
        formatted = template.format()

        # Should include content from shared/common_instructions.yaml
        assert "GENERAL AGENT GUIDELINES:" in formatted

    def test_variable_substitution(self):
        """Test variable substitution in templates."""
        registry = get_prompt_registry()

        # Test with search template
        search_template = registry.get("agents.search")
        formatted = search_template.format(knowledge_base_name="Custom KB", max_search_iterations=5)

        assert "Custom KB" in formatted

    def test_partial_templates(self):
        """Test partial template application."""
        config = PromptConfig(name="test", variables={"var1": "default1", "var2": "default2"})

        template = BasePromptTemplate(config=config, template_content="Var1: {var1}, Var2: {var2}")

        # Create partial with one variable set
        partial = template.partial(var1="fixed")

        # Format with remaining variable
        result = partial.format(var2="dynamic")
        assert result == "Var1: fixed, Var2: dynamic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
