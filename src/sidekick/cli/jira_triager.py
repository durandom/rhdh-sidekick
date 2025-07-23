"""
Jira Triager CLI commands.

This module provides CLI commands for recommending team/component for Jira tickets using RAG.
"""

import typer
from loguru import logger
from rich.console import Console
from ..agents.jira_triager_agent import JiraTriagerAgent
from ..agents.jira_knowledge import JiraKnowledgeManager
from sidekick.utils.jira_client_utils import get_jira_triager_fields, fetch_and_transform_issues, DEFAULT_NUM_ISSUES
import json
import os

console = Console()

jira_triager_app = typer.Typer(
    name="jira-triager",
    help="Recommend team/component for Jira tickets using RAG",
    rich_markup_mode="rich",
)

@jira_triager_app.command()
def triage(
    issue_id: str = typer.Argument(None, help="Jira issue ID (e.g., RHIDP-6496). If provided, fetches fields automatically."),
    title: str = typer.Option(None, help="Title of the Jira issue (overrides fetched title)"),
    description: str = typer.Option(None, help="Description of the Jira issue (overrides fetched description)"),
    component: str = typer.Option(None, help="Component (optional, overrides fetched)"),
    team: str = typer.Option(None, help="Team (optional, overrides fetched)"),
    assignee: str = typer.Option(None, help="Assignee (optional, overrides fetched)"),
    project_key: str = typer.Option(None, help="Project key (optional, overrides fetched)"),
):
    """Triage a Jira issue by ID or manual fields and recommend team/component."""
    jira_knowledge_manager = JiraKnowledgeManager()
    agent = JiraTriagerAgent(jira_knowledge_manager=jira_knowledge_manager)

    def clean_field(val):
        return val if val and str(val).strip() else None

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
            raise typer.Exit(1)
        current_ticket = {
            "title": get_field(title, fetched.get("title", "")),
            "description": get_field(description, fetched.get("description", "")),
            "component": get_field(component, fetched.get("components"), is_list=True),
            "team": get_field(team, fetched.get("team", "")),
            "assignee": get_field(assignee, fetched.get("assignee", "")),
            "project_key": get_field(project_key, fetched.get("project_key", "")),
        }
    else:
        current_ticket = {
            "title": clean_field(title),
            "description": clean_field(description),
            "component": clean_field(component),
            "team": clean_field(team),
            "assignee": clean_field(assignee),
            "project_key": clean_field(project_key),
        }
    result = agent.triage_ticket(current_ticket)
    if result:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        console = Console()
        lines = []
        for k, v in result.items():
            lines.append(f"[bold magenta]{k.capitalize()}:[/bold magenta] [bold white]{v}[/bold white]")
        panel_text = "\n".join(lines)
        console.print(Panel(panel_text, title="Recommended Assignment", title_align="left", border_style="magenta"))

@jira_triager_app.command()
def load_past_jiras(
    projects: str = typer.Option(
        "RHDHSUPP,RHIDP,RHDHBUGS",
        help="Comma-separated list of Jira project keys (default: RHDHSUPP,RHIDP,RHDHBUGS)"
    ),
    jql_extra: str = typer.Option("", help="Extra JQL filter, e.g. 'AND status = \"Resolved\"'"),
    num_issues: int = typer.Option(DEFAULT_NUM_ISSUES, help="Number of issues to return per project (default: 50)")
):
    """Fetch and transform past Jira tickets for one or more projects. Always filters for resolution = Done, and requires team and component."""
    from rich.console import Console
    console = Console()
    built_in_filter = (
        'AND resolution = "Done" '
        'AND resolutiondate >= -360d '
        'AND Team is not EMPTY '
        'AND Team != 4365 '
        'AND component is not EMPTY'
    )
    jql = (jql_extra.strip() + " " + built_in_filter).strip()
    all_issues = []
    for project_key in [p.strip() for p in projects.split(",") if p.strip()]:
        try:
            # Use a temp file for each project
            temp_file = f"_tmp_{project_key}.json"
            fetch_and_transform_issues(
                project_key=project_key,
                jql_extra=jql,
                output_file=temp_file,
                num_issues=num_issues
            )
            with open(temp_file, "r") as f:
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
    output_file = "knowledge/rag/jira/sample_jiras.json"
    with open(output_file, "w") as f:
        json.dump(all_issues, f, indent=2)
    console.print(f"[green]Successfully wrote {len(all_issues)} issues to {output_file}[/green]")

if __name__ == "__main__":
    jira_triager_app() 