"""
Jira client utility functions for the sidekick CLI application.
"""

import json
import os

from loguru import logger

from sidekick.tools.jira import _get_jira_client

DEFAULT_NUM_ISSUES = 50


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


def get_jira_triager_fields(
    issue_id: str,
    *,
    title: str | None = None,
    description: str | None = None,
    component: str | None = None,
    team: str | None = None,
    assignee: str | None = None,
    project_key: str | None = None,
) -> dict:
    """
    Fetch a Jira issue and return a simple "current_ticket" dict.

    Returns keys: key, title, description, component, team, assignee, project_key.
    CLI-provided overrides (if not None) take precedence over fetched values. For
    components, the first component is used.
    """
    jira = _get_jira_client()
    try:
        issue = jira.issue(issue_id, expand="renderedFields,changelog,comments")
    except Exception as e:
        raise ValueError(f"Could not fetch Jira issue {issue_id}: {e}") from e

    fields = issue.fields

    fetched = {
        "title": getattr(fields, "summary", ""),
        "description": getattr(fields, "description", ""),
        "components": [comp.name for comp in getattr(fields, "components", [])]
        if getattr(fields, "components", None)
        else [],
        "team": getattr(getattr(fields, "customfield_12313240", None), "name", None),
        "assignee": fields.assignee.displayName if getattr(fields, "assignee", None) else None,
        "project_key": getattr(getattr(fields, "project", None), "key", None),
    }

    def get_field(cli_value, fetched_value, is_list: bool = False):
        if cli_value is not None:
            return cli_value if cli_value.strip() else None
        if is_list:
            return (fetched_value or [""])[0]
        return fetched_value

    current_ticket = {
        "key": issue_id,
        "title": get_field(title, fetched.get("title", "")),
        "description": get_field(description, fetched.get("description", "")),
        "component": get_field(component, fetched.get("components"), is_list=True),
        "team": get_field(team, fetched.get("team", "")),
        "assignee": get_field(assignee, fetched.get("assignee", "")),
        "project_key": get_field(project_key, fetched.get("project_key", "")),
    }

    return current_ticket


def clean_jira_description(text):
    if not text:
        return ""
    cleaned = text.replace("{noformat}", "")
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "")
    cleaned = cleaned.strip()
    return cleaned


def fetch_and_transform_issues(
    project_key: str, jql_extra: str = "", num_issues: int = DEFAULT_NUM_ISSUES, output_file: str = "examples.json"
):
    """
    Fetch and transform Jira issues for a given project and optional extra JQL filters.
    Args:
        project_key: The Jira project key (e.g., 'RHIDP' or 'RHDHSUPP')
        jql_extra: Additional JQL filter string (e.g., 'AND status = "Resolved"')
        num_issues: Total number of issues to return per project (default 50)
        output_file: File to write the transformed data to
    """
    import json

    jira = _get_jira_client()
    start_at = 0
    transformed_data: list[dict[str, str]] = []
    jql = f'project = "{project_key}" {jql_extra}'.strip()
    total = None
    batch_size = 50  # Default batch size for Jira API calls

    while (total is None or start_at < total) and len(transformed_data) < num_issues:
        remaining = num_issues - len(transformed_data)
        this_batch = min(batch_size, remaining)
        issues = jira.search_issues(
            jql, startAt=start_at, maxResults=this_batch, fields="summary,components,customfield_12313240,description"
        )
        if total is None:
            total = issues.total

        for issue in issues:
            fields = issue.fields
            title = getattr(fields, "summary", "")
            components = getattr(fields, "components", [])
            component = components[0].name if components else ""
            team_field = getattr(fields, "customfield_12313240", None)
            if team_field is not None and hasattr(team_field, "name"):
                team = team_field.name
            elif isinstance(team_field, dict) and "name" in team_field:
                team = team_field["name"]
            elif isinstance(team_field, str):
                team = team_field
            else:
                team = ""
            description = clean_jira_description(getattr(fields, "description", ""))
            key = issue.key
            transformed_data.append(
                {"title": title, "key": key, "component": component, "description": description, "team": team}
            )
            if len(transformed_data) >= num_issues:
                break

        if len(transformed_data) >= num_issues:
            break

        start_at += this_batch

    with open(output_file, "w") as file:
        json.dump(transformed_data, file, indent=2)
    logger.info(f"Wrote {len(transformed_data)} issues to {output_file}")


TEAM_CUSTOM_FIELD_KEY = "customfield_12313240"


def set_issue_field(issue_key: str, field_key: str, field_value: str | list[str]) -> dict:
    """Set the given issue field. Currently supports components and team fields.

    Returns a dict with `updated` (bool), `message` (str) and optional `details`.
    """
    try:
        jira = _get_jira_client()
        issue = jira.issue(issue_key)
    except Exception as e:
        return {"updated": False, "message": f"Could not fetch issue {issue_key}: {e}"}

    try:
        if field_key == "components":
            payload_value = [{"name": str(x)} for x in field_value]
        elif field_key == TEAM_CUSTOM_FIELD_KEY:
            raw_team_id_map = os.getenv("TEAM_ID_MAP")
            if not raw_team_id_map:
                raise ValueError("TEAM_ID_MAP environment variable is required")
            name_to_id = json.loads(raw_team_id_map)
            team_id = name_to_id.get(field_value)
            if not team_id:
                raise ValueError(f"Team '{field_value}' not found in TEAM_ID_MAP")
            payload_value = team_id
        else:
            return {"updated": False, "message": f"Update failed: field_key '{field_key}' not supported"}

        issue.update(fields={field_key: payload_value})
        return {"updated": True, "message": "Updated", "details": {field_key: payload_value}}
    except Exception as e:
        return {"updated": False, "message": f"Update failed: {e}", "details": {field_key: field_value}}
