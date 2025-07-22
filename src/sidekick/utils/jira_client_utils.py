"""
Jira client utility functions for the sidekick CLI application.
"""

from loguru import logger
from sidekick.tools.jira import _get_jira_client


def get_project_component_names(project_key: str) -> list[str]:
    """
    Return the list of component names for the given Jira project key.
    Args:
        project_key: The Jira project key (e.g., 'RHIDP')
    Returns:
        List of component names (str)
    """
    jira = _get_jira_client()
    try:
        components = jira.project_components(project_key)
        return [comp.name for comp in components]
    except Exception as e:
        logger.error(f"Failed to fetch components for project {project_key}: {e}")
        return [] 



def get_jira_triager_fields(issue_id: str) -> dict:
    """
    Fetch a Jira issue by ID and return its key fields as a dictionary.

    Args:
        issue_id: The Jira issue key (e.g., PROJ-123)

    Returns:
        dict with keys: title, description, components, team (if available), assignee
    """
    jira = _get_jira_client()
    try:
        issue = jira.issue(issue_id, expand="renderedFields,changelog,comments")
    except Exception as e:
        raise ValueError(f"Could not fetch Jira issue {issue_id}: {e}")

    # Extract fields directly
    title = getattr(issue.fields, "summary", "")
    description = getattr(issue.fields, "description", "")
    components = [comp.name for comp in getattr(issue.fields, "components", [])] if getattr(issue.fields, "components", None) else []
    assignee = issue.fields.assignee.displayName if getattr(issue.fields, "assignee", None) else None
    team = getattr(issue.fields, "customfield_12313240", None)

    return {
        "title": title,
        "description": description,
        "components": components,
        "team": team,
        "assignee": assignee,
    }
