"""
Jira Triager CLI commands.

This module provides CLI commands for recommending team/component for Jira tickets using RAG.
"""

import typer
from loguru import logger
from rich.console import Console
from ..agents.jira_triager_agent import JiraTriagerAgent
from ..agents.jira_knowledge import JiraKnowledgeManager

console = Console()

jira_triager_app = typer.Typer(
    name="jira-triager",
    help="Recommend team/component for Jira tickets using RAG",
    rich_markup_mode="rich",
)

@jira_triager_app.command()
def triage(
    title: str = typer.Option(..., help="Title of the Jira ticket"),
    description: str = typer.Option(..., help="Description of the Jira ticket"),
    assignee: str = typer.Option("", help="Assignee (if already assigned)"),
    component: str = typer.Option("", help="Component (if already assigned)"),
    team: str = typer.Option("", help="Team (if already assigned)"),
) -> None:
    """
    Recommend the best team/component for a Jira ticket using RAG over historical tickets.

    Example:
        sidekick jira-triager triage --title "Password reset fails" --description "Reset link returns 500 error." --component "Authentication"
    """
    logger.debug(f"Triage called with title={title}, description={description}, assignee={assignee}, component={component}, team={team}")
    current_ticket = {
        "title": title,
        "description": description,
        "assignee": assignee,
        "component": component,
        "team": team,
    }
    jira_knowledge_manager = JiraKnowledgeManager()
    agent = JiraTriagerAgent(jira_knowledge_manager=jira_knowledge_manager)
    result = agent.triage_ticket(current_ticket)
    console.print("[bold green]Recommended assignment:[/bold green]", result)

if __name__ == "__main__":
    jira_triager_app() 