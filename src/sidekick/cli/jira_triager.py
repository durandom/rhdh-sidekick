"""
Jira Triager CLI commands.

This module provides CLI commands for recommending team/component for Jira tickets using RAG.
"""

import json
import os

import typer
from rich.console import Console
from rich.table import Table

from sidekick.tools.jira import _get_jira_client
from sidekick.utils.jira_client_utils import DEFAULT_NUM_ISSUES, fetch_and_transform_issues, get_jira_triager_fields

from ..agents.jira_knowledge import JiraKnowledgeManager
from ..agents.jira_triager_agent import JiraTriagerAgent

JIRA_FILTER = (
    '(project = RHIDP OR project in ("Red Hat Developer Hub Bugs", rhdhsupp)) '
    "AND status != closed AND (Team is EMPTY OR component is EMPTY) "
    'AND issuetype not in (Sub-task, Epic, Feature, "Feature Request", Outcome) '
    "ORDER BY created DESC, priority DESC"
)
console = Console()

jira_triager_app = typer.Typer(
    name="jira-triager",
    help="Recommend team/component for Jira tickets using RAG",
    rich_markup_mode="rich",
)


@jira_triager_app.command()
def load_jira_knowledge(
    projects: str = typer.Option(
        "RHDHSUPP,RHIDP,RHDHBUGS", help="Comma-separated list of Jira project keys (default: RHDHSUPP,RHIDP,RHDHBUGS)"
    ),
    jql_extra: str = typer.Option("", help="Extra JQL filter, e.g. 'AND status = \"Resolved\"'"),
    num_issues: int = typer.Option(DEFAULT_NUM_ISSUES, help="Number of issues to return per project (default: 100)"),
):
    """Fetch and transform past Jira tickets for one or more projects.

    Always filters for resolution = Done, and requires team and component.
    """
    from rich.console import Console

    console = Console()
    built_in_filter = (
        'AND resolution = "Done" '
        "AND resolutiondate >= -360d "
        "AND Team is not EMPTY "
        "AND Team != 4365 "
        "AND component is not EMPTY"
    )
    jql = (jql_extra.strip() + " " + built_in_filter).strip()
    all_issues = []
    for project_key in [p.strip() for p in projects.split(",") if p.strip()]:
        try:
            # Use a temp file for each project
            temp_file = f"_tmp_{project_key}.json"
            fetch_and_transform_issues(
                project_key=project_key, jql_extra=jql, output_file=temp_file, num_issues=num_issues
            )
            with open(temp_file) as f:
                issues = json.load(f)
            all_issues.extend(issues)
        except Exception as e:
            console.print(f"[yellow]Warning: Error fetching issues for {project_key}: {e}[/yellow]")
        finally:
            # Delete the temp file if it exists
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as del_err:
                console.print(f"[yellow]Warning: Could not delete temp file {temp_file}: {del_err}[/yellow]")
    # Write combined issues to the fixed output file
    output_file = "tmp/jira_knowledge_base.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(all_issues, f, indent=2)
    console.print(f"[green]Successfully wrote {len(all_issues)} issues to {output_file}[/green]")


@jira_triager_app.command()
def triage(
    issue_id: str = typer.Argument(
        None,
        help="Jira issue ID (e.g., RHIDP-6496). If provided, fetches fields automatically, "
        "otherwise all filtered issues will be triaged.",
    ),
    title: str = typer.Option(None, help="Title of the Jira issue (overrides fetched title)"),
    description: str = typer.Option(None, help="Description of the Jira issue (overrides fetched description)"),
    component: str = typer.Option(None, help="Component (optional, overrides fetched)"),
    team: str = typer.Option(None, help="Team (optional, overrides fetched)"),
    assignee: str = typer.Option(None, help="Assignee (optional, overrides fetched)"),
    project_key: str = typer.Option(None, help="Project key (optional, overrides fetched)"),
):
    """Triage a Jira issue by ID or manual fields and recommend team/component."""
    console = Console()
    jira_knowledge_manager = JiraKnowledgeManager()
    agent = JiraTriagerAgent(jira_knowledge_manager=jira_knowledge_manager)

    def get_field(cli_value, fetched_value, is_list=False):
        # If the CLI option was provided (even as empty string), use it (cleaned)
        if cli_value is not None:
            val = cli_value if cli_value.strip() else None
            return val
        # Otherwise, use the fetched value
        if is_list:
            return (fetched_value or [""])[0]
        return fetched_value

    if issue_id:
        try:
            fetched = get_jira_triager_fields(issue_id)
        except Exception as e:
            typer.echo(f"Error fetching Jira issue: {e}")
            raise typer.Exit(1) from e
        current_ticket = {
            "title": get_field(title, fetched.get("title", "")),
            "description": get_field(description, fetched.get("description", "")),
            "component": get_field(component, fetched.get("components"), is_list=True),
            "team": get_field(team, fetched.get("team", "")),
            "assignee": get_field(assignee, fetched.get("assignee", "")),
            "project_key": get_field(project_key, fetched.get("project_key", "")),
        }
        result = agent.triage_ticket(current_ticket)
        if result:
            from rich.panel import Panel

            lines = []
            confidence = result.get("confidence", 0.0)

            for k, v in result.items():
                if k == "confidence":
                    lines.append(f"[bold yellow]Confidence:[/bold yellow] [bold white]{v:.2f}[/bold white]")
                else:
                    lines.append(f"[bold magenta]{k.capitalize()}:[/bold magenta] [bold white]{v}[/bold white]")

            panel_text = "\n".join(lines)
            console.print(Panel(panel_text, title="Recommended Assignment", title_align="left", border_style="magenta"))

    else:
        jira_knowledge_manager = JiraKnowledgeManager()
        agent = JiraTriagerAgent(jira_knowledge_manager=jira_knowledge_manager)

        jira = _get_jira_client()
        issues = jira.search_issues(JIRA_FILTER, maxResults=100)
        table = Table(title="Jira Triager Results")
        table.add_column("Issue Key", style="cyan", no_wrap=True)
        table.add_column("Team Assignment", style="magenta")
        table.add_column("Component Assignment", style="green")
        table.add_column("Confidence", style="yellow", justify="center")

        for issue in issues:
            try:
                fetched = get_jira_triager_fields(issue)
            except Exception as e:
                typer.echo(f"Error fetching Jira issue: {e}")
                raise typer.Exit(1) from e
            current_ticket = {
                "key": issue.key,
                "title": fetched.get("title", ""),
                "description": fetched.get("description", ""),
                "component": fetched.get("components", ""),
                "team": fetched.get("team", ""),
                "assignee": fetched.get("assignee", ""),
                "project_key": fetched.get("project_key", ""),
            }
            result = agent.triage_ticket(current_ticket)

            # Determine what to display for each field
            team_display = (
                result.get("team", "")
                if result.get("team")
                else "[dim]Assigned[/dim]"
                if current_ticket.get("team")
                else ""
            )
            component_display = (
                result.get("component", "")
                if result.get("component")
                else "[dim]Assigned[/dim]"
                if current_ticket.get("component")
                else ""
            )

            # Format confidence score
            confidence = result.get("confidence", 0.0)
            if result.get("team") or result.get("component"):  # Only show confidence if there are recommendations
                confidence_display = f"{confidence:.2f}"
            elif current_ticket.get("team") and current_ticket.get("component"):
                confidence_display = "[dim]N/A[/dim]"  # Both fields already assigned
            else:
                confidence_display = ""  # Empty fields, no recommendations

            table.add_row(issue.key, team_display, component_display, confidence_display)

        console.print()
        console.print(table)


@jira_triager_app.command()
def info() -> None:
    """Show information about the Jira Triager feature."""
    from rich.console import Console

    console = Console()
    console.print("[bold blue]Jira Triager Agent[/bold blue]")
    console.print(
        "\nThis tool uses a Retrieval-Augmented Generation (RAG) workflow: it leverages "
        "a local knowledge base of historical Jira issues and a large language model (LLM) "
        "to recommend the best team and component for new Jira tickets. The agent performs "
        "semantic search over past issues to provide context-aware, data-driven triage recommendations."
    )

    console.print("\n[bold]Workflow:[/bold]")
    console.print(
        "  1. [bold]Extract Jira Data for RAG-Powered Triage[/bold]:\n     "
        "Run [green]sidekick jira-triager load-jira-knowledge[/green] to build the local "
        "knowledge base from historical Jira issues. This must be done before triaging."
    )
    console.print(
        "  2. [bold]Triage Jira Issues Using the RAG Agent[/bold]:\n     "
        "Run [green]sidekick jira-triager triage[/green] to get team/component "
        "recommendations for a Jira issue."
    )

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • GOOGLE_API_KEY - Google AI/Gemini API key")
    console.print("  • JIRA_PERSONAL_TOKEN - Jira API token")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  uv run sidekick jira-triager load-jira-knowledge [OPTIONS]")
    console.print("  uv run sidekick jira-triager triage [OPTIONS]")
    console.print("  uv run sidekick jira-triager triage RHIDP-6496")
    console.print("  uv run sidekick jira-triager triage RHIDP-6496 --component 'Authentication' --team ''")
    console.print(
        "  uv run sidekick jira-triager triage --title 'Password reset fails' "
        "--description 'Reset link returns 500 error.'"
    )
