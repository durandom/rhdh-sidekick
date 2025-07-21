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
    title: str = typer.Option("", help="Title of the Jira issue (overrides fetched title)"),
    description: str = typer.Option("", help="Description of the Jira issue (overrides fetched description)"),
    component: str = typer.Option("", help="Component (optional, overrides fetched)"),
    team: str = typer.Option("", help="Team (optional, overrides fetched)"),
    assignee: str = typer.Option("", help="Assignee (optional, overrides fetched)"),
):
    """Triage a Jira issue by ID or manual fields and recommend team/component."""
    jira_knowledge_manager = JiraKnowledgeManager()
    agent = JiraTriagerAgent(jira_knowledge_manager=jira_knowledge_manager)

    if issue_id:
        try:
            fetched = get_jira_triager_fields(issue_id)
        except Exception as e:
            typer.echo(f"Error fetching Jira issue: {e}")
            raise typer.Exit(1)
        current_ticket = {
            "title": title or fetched.get("title", ""),
            "description": description or fetched.get("description", ""),
            "component": component or (fetched.get("components") or [""])[0],
            "team": team or fetched.get("team", ""),
            "assignee": assignee or fetched.get("assignee", ""),
        }
    else:
        current_ticket = {
            "title": title,
            "description": description,
            "component": component,
            "team": team,
            "assignee": assignee,
        }
    result = agent.triage_ticket(current_ticket)
    if result:
        typer.echo(f"Recommended assignment: {result}")

if __name__ == "__main__":
    jira_triager_app() 