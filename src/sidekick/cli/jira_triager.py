"""
Jira Triager CLI commands.

This module provides CLI commands for recommending team/component for Jira tickets using RAG.
"""

import typer
from loguru import logger
from rich.console import Console
from ..agents.jira_triager_agent import JiraTriagerAgent
from ..agents.jira_knowledge import JiraKnowledgeManager
from sidekick.tools.jira import get_jira_triager_fields

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
        }
    else:
        current_ticket = {
            "title": clean_field(title),
            "description": clean_field(description),
            "component": clean_field(component),
            "team": clean_field(team),
            "assignee": clean_field(assignee),
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

if __name__ == "__main__":
    jira_triager_app() 