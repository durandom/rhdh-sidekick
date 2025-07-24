#!/usr/bin/env python3
"""
Demonstration of the LangChain prompt template system in Sidekick.

This example shows how to:
1. Load and use prompt templates
2. Customize templates with variables
3. Compose templates from multiple sources
4. Create custom templates programmatically
"""

from pathlib import Path

from loguru import logger
from rich.console import Console

from sidekick.prompts import (
    BasePromptTemplate,
    PromptConfig,
    get_prompt_registry,
)

console = Console()


def demo_basic_usage():
    """Demonstrate basic prompt template usage."""
    console.print("\n[bold cyan]1. Basic Template Usage[/bold cyan]")

    # Load a template from the registry
    registry = get_prompt_registry()
    search_template = registry.get("agents.search")

    # Get formatted instructions
    instructions = search_template.get_instructions_list()
    console.print(f"Loaded {len(instructions)} instruction sections")
    console.print(f"First section preview: {instructions[0][:100]}...")


def demo_variable_substitution():
    """Demonstrate variable substitution in templates."""
    console.print("\n[bold cyan]2. Variable Substitution[/bold cyan]")

    # Load JIRA template
    registry = get_prompt_registry()
    jira_template = registry.get("agents.jira")

    # Use with custom variables
    custom_instructions = jira_template.format(
        jira_instance="https://mycompany.atlassian.net", default_project="SIDEKICK"
    )

    console.print("Custom JIRA instructions (first 200 chars):")
    console.print(custom_instructions[:200] + "...")


def demo_template_composition():
    """Demonstrate composing templates from multiple sources."""
    console.print("\n[bold cyan]3. Template Composition[/bold cyan]")

    # Create a custom template that extends existing ones
    config = PromptConfig(
        name="custom_agent",
        version="1.0",
        description="Custom agent with combined features",
        variables={"team_name": "DevOps Team"},
    )

    custom_template = BasePromptTemplate(
        config=config,
        template_content="""
CUSTOM AGENT FOR {team_name}:
This agent combines search and task management capabilities.

SPECIAL FEATURES:
- Advanced search with custom filters
- Automated task creation from search results
- Integration with team workflows
""",
    )

    # Merge with existing template
    registry = get_prompt_registry()
    search_template = registry.get("agents.search")
    combined = custom_template.merge_with(search_template)

    formatted = combined.format(team_name="Platform Engineering")
    console.print(f"Combined template has {len(formatted)} characters")


def demo_dynamic_templates():
    """Demonstrate creating templates dynamically."""
    console.print("\n[bold cyan]4. Dynamic Template Creation[/bold cyan]")

    # Create a template programmatically based on configuration
    def create_environment_template(env: str, features: list[str]) -> BasePromptTemplate:
        feature_list = "\n".join(f"- {feature}" for feature in features)

        config = PromptConfig(name=f"{env}_agent", description=f"Agent for {env} environment")

        template_content = f"""
ENVIRONMENT-SPECIFIC AGENT ({env.upper()}):
This agent is configured for the {env} environment.

ENABLED FEATURES:
{feature_list}

ENVIRONMENT RULES:
- {"Allow direct database access" if env == "development" else "No direct database access"}
- {"Verbose logging enabled" if env == "development" else "Standard logging"}
- {"Can modify configuration" if env != "production" else "Read-only configuration"}
"""

        return BasePromptTemplate(config=config, template_content=template_content)

    # Create templates for different environments
    dev_template = create_environment_template("development", ["debugging", "profiling", "hot-reload"])
    prod_template = create_environment_template("production", ["monitoring", "alerting", "audit-logging"])

    console.print("Development template preview:")
    console.print(dev_template.format()[:300] + "...")

    console.print("\nProduction template preview:")
    console.print(prod_template.format()[:300] + "...")


def demo_template_partial():
    """Demonstrate partial template application."""
    console.print("\n[bold cyan]5. Partial Template Application[/bold cyan]")

    # Create a template with multiple variables
    config = PromptConfig(
        name="api_agent",
        variables={"api_endpoint": "https://api.example.com", "api_version": "v1", "rate_limit": "100 requests/minute"},
    )

    template = BasePromptTemplate(
        config=config,
        template_content="""
API AGENT CONFIGURATION:
- Endpoint: {api_endpoint}
- Version: {api_version}
- Rate Limit: {rate_limit}

Always respect the rate limit when making API calls.
""",
    )

    # Create a partial with some variables pre-filled
    prod_partial = template.partial(api_endpoint="https://api.production.com", api_version="v2")

    # Now only need to provide remaining variables
    final = prod_partial.format(rate_limit="1000 requests/minute")
    console.print("Partial template result:")
    console.print(final)


def main():
    """Run all demonstrations."""
    console.print("[bold green]Sidekick Prompt Template System Demo[/bold green]")
    console.print("=" * 50)

    # Ensure templates directory exists
    templates_dir = Path(__file__).parent.parent / "src" / "sidekick" / "prompts" / "templates"
    if not templates_dir.exists():
        console.print(f"[yellow]Warning: Templates directory not found at {templates_dir}[/yellow]")
        console.print("Creating example templates for demo...")
        # In a real scenario, templates would already exist

    try:
        demo_basic_usage()
        demo_variable_substitution()
        demo_template_composition()
        demo_dynamic_templates()
        demo_template_partial()

        console.print("\n[bold green]✓ All demonstrations completed successfully![/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error during demo: {e}[/bold red]")
        logger.exception("Demo failed")


if __name__ == "__main__":
    main()
