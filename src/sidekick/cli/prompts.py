"""
CLI commands for managing prompt templates.
"""

import builtins
from pathlib import Path

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from ..prompts import get_prompt_registry
from ..prompts.loaders import load_prompt_template

console = Console()

# Create the prompts sub-application
prompts_app = typer.Typer(
    name="prompts",
    help="Manage prompt templates",
    rich_markup_mode="rich",
)


@prompts_app.command()
def list(refresh: bool = typer.Option(False, "--refresh", "-r", help="Refresh template cache")):
    """List all available prompt templates."""
    registry = get_prompt_registry()

    if refresh:
        registry.clear()
        registry.auto_discover()
        console.print("[green]✓[/green] Template cache refreshed")

    templates = registry.list_templates()

    if not templates:
        console.print("[yellow]No templates found[/yellow]")
        return

    table = Table(title="Available Prompt Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description")

    for template_name in templates:
        try:
            template = registry.get(template_name)
            table.add_row(
                template_name, template.config.version, template.config.description or "[dim]No description[/dim]"
            )
        except Exception as e:
            table.add_row(template_name, "[red]Error[/red]", f"[red]{str(e)}[/red]")

    console.print(table)


@prompts_app.command()
def show(
    name: str = typer.Argument(..., help="Template name (e.g., 'agents.search')"),
    format_vars: bool = typer.Option(False, "--format", "-f", help="Show formatted output"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Show raw template content"),
):
    """Show details of a specific prompt template."""
    try:
        registry = get_prompt_registry()
        template = registry.get(name)

        console.print(f"\n[bold cyan]Template: {name}[/bold cyan]")
        console.print(f"Version: {template.config.version}")
        console.print(f"Description: {template.config.description or '[dim]No description[/dim]'}")

        if template.config.variables:
            console.print("\n[bold]Variables:[/bold]")
            for var_name, default in template.config.variables.items():
                console.print(f"  - {var_name}: {default}")

        console.print("\n[bold]Content:[/bold]")

        if raw:
            # Show raw template with variable placeholders
            syntax = Syntax(template.template_content, "yaml", theme="monokai", line_numbers=True)
            console.print(syntax)
        elif format_vars:
            # Show formatted with default variables
            formatted = template.format()
            syntax = Syntax(formatted, "markdown", theme="monokai", line_numbers=True)
            console.print(syntax)
        else:
            # Show as instruction list
            instructions = template.get_instructions_list()
            for i, instruction in enumerate(instructions, 1):
                console.print(f"\n[bold]{i}.[/bold] {instruction}")

    except KeyError:
        console.print(f"[red]Template '{name}' not found[/red]")
        console.print("\nAvailable templates:")
        registry = get_prompt_registry()
        for t in registry.list_templates():
            console.print(f"  - {t}")
    except Exception as e:
        console.print(f"[red]Error loading template: {e}[/red]")


@prompts_app.command()
def validate(
    path: Path | None = typer.Argument(None, help="Path to template file or directory"),
):
    """Validate prompt template files."""
    if path is None:
        # Validate all templates in the default directory
        path = Path(__file__).parent.parent / "prompts" / "templates"

    if not path.exists():
        console.print(f"[red]Path does not exist: {path}[/red]")
        raise typer.Exit(1)

    # Find all YAML files
    if path.is_file():
        files: builtins.list[Path] = [path]
    else:
        yaml_files = builtins.list(path.glob("**/*.yaml"))
        yml_files = builtins.list(path.glob("**/*.yml"))
        files = yaml_files + yml_files

    if not files:
        console.print("[yellow]No template files found[/yellow]")
        return

    errors = 0
    for file in files:
        try:
            template = load_prompt_template(file)
            # Try to format to catch any variable issues
            _ = template.format()
            console.print(f"[green]✓[/green] {file.relative_to(path.parent if path.is_file() else path)}")
        except Exception as e:
            errors += 1
            console.print(f"[red]✗[/red] {file.relative_to(path.parent if path.is_file() else path)}: {e}")

    if errors == 0:
        console.print(f"\n[green]All {len(files)} templates are valid![/green]")
    else:
        console.print(f"\n[red]{errors} template(s) have errors[/red]")


@prompts_app.command()
def create(
    name: str = typer.Argument(..., help="Template name (e.g., 'my_agent')"),
    output_dir: Path | None = typer.Option(
        None, "--output-dir", "-o", help="Output directory (defaults to templates/agents/)"
    ),
):
    """Create a new prompt template from a starter template."""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "prompts" / "templates" / "agents"

    output_file = output_dir / f"{name}.yaml"

    if output_file.exists():
        console.print(f"[red]Template already exists: {output_file}[/red]")
        raise typer.Exit(1)

    # Create starter template
    starter_content = f"""name: {name}_agent
version: "1.0"
description: "TODO: Add description for {name} agent"

# Define variables that can be customized
variables:
  example_var: "default_value"

# Include shared instructions
includes:
  - shared/common_instructions.yaml

# Main template content
template: |
  You are a helpful AI assistant for {name}.

  TODO: Add your agent-specific instructions here.

  Example variable usage: {{example_var}}

  CAPABILITIES:
  - TODO: List what this agent can do

  GUIDELINES:
  - TODO: Add specific guidelines for this agent
"""

    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write template
    output_file.write_text(starter_content)

    console.print(f"[green]✓[/green] Created template: {output_file}")
    console.print("\nNext steps:")
    console.print("1. Edit the template file to add your instructions")
    console.print("2. Update your agent to use get_agent_instructions_from_template()")
    console.print(f"3. Test with: sidekick prompts show agents.{name}")


if __name__ == "__main__":
    prompts_app()
