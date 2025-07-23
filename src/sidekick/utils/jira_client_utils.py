"""
Jira client utility functions for the sidekick CLI application.
"""

from loguru import logger
from sidekick.tools.jira import _get_jira_client

DEFAULT_NUM_ISSUES = 100

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


def fetch_and_transform_issues(
    project_key: str,
    jql_extra: str = "",
    num_issues: int = DEFAULT_NUM_ISSUES,
    output_file: str = "examples.json"
):
    """
    Fetch and transform Jira issues for a given project and optional extra JQL filters.
    Args:
        project_key: The Jira project key (e.g., 'RHIDP' or 'RHDHSUPP')
        jql_extra: Additional JQL filter string (e.g., 'AND status = "Resolved"')
        num_issues: Total number of issues to return per project (default 100)
        output_file: File to write the transformed data to
    """
    import json
    jira = _get_jira_client()
    start_at = 0
    transformed_data = []
    jql = f'project = "{project_key}" {jql_extra}'.strip()
    total = None
    batch_size = 50 # Default batch size for Jira API calls

    while (total is None or start_at < total) and len(transformed_data) < num_issues:
        remaining = num_issues - len(transformed_data)
        this_batch = min(batch_size, remaining)
        issues = jira.search_issues(
            jql,
            startAt=start_at,
            maxResults=this_batch,
            fields="summary,components,customfield_12313240,description"
        )
        if total is None:
            total = issues.total

        for issue in issues:
            fields = issue.fields
            title = getattr(fields, "summary", "")
            components = getattr(fields, "components", [])
            component = components[0].name if components else ""
            team_field = getattr(fields, "customfield_12313240", None)
            if hasattr(team_field, "name"):
                team = team_field.name
            elif isinstance(team_field, dict) and "name" in team_field:
                team = team_field["name"]
            elif isinstance(team_field, str):
                team = team_field
            else:
                team = ""
            description = getattr(fields, "description", "")
            key = issue.key
            transformed_data.append({
                "title": title,
                "key": key,
                "component": component,
                "description": description,
                "team": team
            })
            if len(transformed_data) >= num_issues:
                break

        if len(transformed_data) >= num_issues:
            break

        start_at += this_batch

    with open(output_file, "w") as file:
        json.dump(transformed_data, file, indent=2)
    logger.info(f"Wrote {len(transformed_data)} issues to {output_file}")
