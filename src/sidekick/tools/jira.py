"""
Jira toolkit for interacting with Jira issues and projects.
"""

import json
import os
import re
from typing import Any

from agno.tools import Toolkit
from loguru import logger
from pydantic import BaseModel, Field

try:
    from jira import JIRA, Issue
except ImportError:
    raise ImportError("`jira` not installed. Please install using `pip install jira`") from None


class JiraCommentData(BaseModel):
    """Pydantic model for Jira comment data."""

    id: str | None = Field(None, description="Comment ID")
    author: str = Field(..., description="Comment author display name")
    created: str = Field(..., description="Comment creation timestamp")
    body: str = Field(..., description="Comment body text")
    pr_urls_found: list[str] = Field(default_factory=list, description="GitHub PR URLs found in comment")


class JiraIssueData(BaseModel):
    """Pydantic model for Jira issue data."""

    key: str = Field(..., description="Jira ticket key (e.g., PROJ-123)")
    summary: str = Field(..., description="Ticket summary/title")
    description: str = Field(..., description="Ticket description content")
    status: str = Field(..., description="Current ticket status")
    priority: str = Field(..., description="Priority level of the ticket")
    assignee: str | None = Field(None, description="Assigned user display name")
    reporter: str | None = Field(None, description="Reporter user display name")
    created_date: str | None = Field(None, description="Ticket creation timestamp")
    updated_date: str | None = Field(None, description="Last update timestamp")
    components: list[str] = Field(default_factory=list, description="Affected components")
    labels: list[str] = Field(default_factory=list, description="Ticket labels")
    pull_requests: list[str] = Field(default_factory=list, description="GitHub PR URLs found in ticket")
    comments: list[JiraCommentData] | None = Field(None, description="All ticket comments with PR URLs extracted")
    custom_fields: dict[str, Any] | None = Field(None, description="Custom Jira fields like release notes")


def _get_jira_client() -> JIRA:
    """
    Create and return a JIRA client instance.

    Returns:
        JIRA: Configured JIRA client instance

    Raises:
        ValueError: If required environment variables are not set
    """
    server_url = os.getenv("JIRA_URL")
    username = os.getenv("JIRA_USERNAME")
    token = os.getenv("JIRA_PERSONAL_TOKEN")

    logger.debug(f"Initializing JIRA client with server_url: {server_url}")
    logger.debug(f"Username provided: {'Yes' if username else 'No'}")
    logger.debug(f"Token provided: {'Yes' if token else 'No'}")

    if not server_url:
        raise ValueError("JIRA_URL environment variable is required")

    if not token:
        raise ValueError("JIRA_PERSONAL_TOKEN environment variable is required")

    logger.debug(f"Connecting to Jira at {server_url}")

    # Use token authentication
    try:
        if username and token:
            logger.debug("Using basic auth (username + token)")
            client = JIRA(server=server_url, basic_auth=(username, token))
        else:
            logger.debug("Using token auth")
            client = JIRA(server=server_url, token_auth=token)

        logger.debug("Successfully created JIRA client")
        return client
    except Exception as e:
        logger.error(f"Failed to create JIRA client: {e}")
        raise


class JiraTools(Toolkit):
    """Toolkit for interacting with Jira issues, projects, and comments."""

    def __init__(
        self,
        get_issue: bool = True,
        search_issues: bool = True,
        add_comment: bool = False,
        create_issue: bool = False,
        **kwargs,
    ):
        """Initialize Jira toolkit.

        Args:
            get_issue: Include get_issue tool (default: True)
            search_issues: Include search_issues tool (default: True)
            add_comment: Include add_comment tool (default: False)
            create_issue: Include create_issue tool (default: False)
            **kwargs: Additional arguments passed to parent Toolkit
        """
        # Initialize JIRA client once
        self._jira_client = None

        tools: list[Any] = []
        if get_issue:
            tools.append(self.get_issue)
        if search_issues:
            tools.append(self.search_issues)
        if add_comment:
            tools.append(self.add_comment)
        if create_issue:
            tools.append(self.create_issue)

        super().__init__(name="jira_tools", tools=tools, **kwargs)

    def _get_jira_client(self) -> JIRA:
        """Get or create JIRA client instance."""
        if self._jira_client is None:
            server_url = os.getenv("JIRA_URL")
            username = os.getenv("JIRA_USERNAME")
            token = os.getenv("JIRA_PERSONAL_TOKEN")

            logger.debug(f"Initializing JIRA client with server_url: {server_url}")
            logger.debug(f"Username provided: {'Yes' if username else 'No'}")
            logger.debug(f"Token provided: {'Yes' if token else 'No'}")

            if not server_url:
                raise ValueError("JIRA_URL environment variable is required")

            if not token:
                raise ValueError("JIRA_PERSONAL_TOKEN environment variable is required")

            logger.debug(f"Connecting to Jira at {server_url}")

            try:
                if username and token:
                    logger.debug("Using basic auth (username + token)")
                    self._jira_client = JIRA(server=server_url, basic_auth=(username, token))
                else:
                    logger.debug("Using token auth")
                    self._jira_client = JIRA(server=server_url, token_auth=token)

                logger.debug("Successfully created JIRA client")
            except Exception as e:
                logger.error(f"Failed to create JIRA client: {e}")
                raise

        return self._jira_client

    def _extract_github_pr_urls(self, text: str) -> list[str]:
        """Extract GitHub PR URLs from text.

        Args:
            text: Text to search for GitHub PR URLs

        Returns:
            List of GitHub PR URLs found in the text
        """
        if not text:
            return []

        # Pattern to match GitHub PR URLs
        pattern = r"https://github\.com/[^/\s]+/[^/\s]+/pull/\d+"
        matches = re.findall(pattern, text, re.IGNORECASE)

        return list(set(matches))  # Remove duplicates

    def _format_issue_details(self, issue: Issue) -> JiraIssueData:
        """
        Format JIRA issue details into a structured JiraIssueData object.

        Args:
            issue: JIRA Issue object

        Returns:
            JiraIssueData object with formatted issue details
        """
        logger.debug(f"Formatting issue details for {issue.key}")

        # Extract basic fields
        details = {
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description or "",
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "Unknown",
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
            "reporter": issue.fields.reporter.displayName if issue.fields.reporter else None,
            "created_date": str(issue.fields.created) if issue.fields.created else None,
            "updated_date": str(issue.fields.updated) if issue.fields.updated else None,
            "components": [comp.name for comp in issue.fields.components] if issue.fields.components else [],
            "labels": list(issue.fields.labels) if issue.fields.labels else [],
        }

        logger.debug(f"Basic fields extracted for {issue.key}: {len(details)} fields")

        # Extract GitHub PR URLs from description
        pr_urls = self._extract_github_pr_urls(details["description"])
        logger.debug(f"Found {len(pr_urls)} PR URLs in description")

        # Extract comments and their content for PR URLs
        comments_data = []
        try:
            if hasattr(issue.fields, "comment") and hasattr(issue.fields.comment, "comments"):
                comments = issue.fields.comment.comments
                logger.debug(f"Processing {len(comments)} comments for {issue.key}")

                for comment in comments:
                    if hasattr(comment, "body") and comment.body:
                        comment_pr_urls = self._extract_github_pr_urls(comment.body)
                        pr_urls.extend(comment_pr_urls)

                        # Store comment data using Pydantic model
                        comment_data = JiraCommentData(
                            id=getattr(comment, "id", None),
                            author=getattr(getattr(comment, "author", {}), "displayName", "Unknown"),
                            created=str(getattr(comment, "created", "")),
                            body=comment.body,
                            pr_urls_found=comment_pr_urls,
                        )
                        comments_data.append(comment_data)

                        if comment_pr_urls:
                            logger.debug(f"Found {len(comment_pr_urls)} PR URLs in comment {comment.id}")
            else:
                logger.debug(f"No comments found for {issue.key}")
        except (AttributeError, Exception) as e:
            logger.debug(f"Could not extract comments from issue {issue.key}: {e}")

        # Check for custom PR field (customfield_12310220)
        pr_data = None
        try:
            pr_data = getattr(issue.fields, "customfield_12310220", None)
            logger.debug(f"Custom PR field data for {issue.key}: {pr_data}")

            if pr_data:
                if isinstance(pr_data, list) and pr_data:
                    # If it's a list, process each element
                    for item in pr_data:
                        if isinstance(item, str) and item.startswith("https://github.com"):
                            pr_urls.append(item)
                            logger.debug(f"Found PR URL in custom field list: {item}")
                elif isinstance(pr_data, str) and pr_data.startswith("https://github.com"):
                    pr_urls.append(pr_data)
                    logger.debug(f"Found PR URL in custom field: {pr_data}")
        except (AttributeError, Exception) as e:
            logger.debug(f"Could not extract custom PR field from issue {issue.key}: {e}")

        # Add custom fields section for additional metadata
        custom_fields = {}
        try:
            # Release note text (customfield_12317313)
            release_note_text = getattr(issue.fields, "customfield_12317313", None)
            if release_note_text:
                custom_fields["release_note_text"] = release_note_text
                logger.debug(f"Found release note text for {issue.key}")

            # Release note status (customfield_12310213)
            release_note_status = getattr(issue.fields, "customfield_12310213", None)
            if release_note_status:
                if hasattr(release_note_status, "get"):
                    status_value = release_note_status.get("value")
                else:
                    status_value = str(release_note_status)
                custom_fields["release_note_status"] = status_value
                logger.debug(f"Found release note status for {issue.key}: {status_value}")

            # PR data field (customfield_12310220)
            if pr_data:
                custom_fields["pr_data"] = pr_data
                logger.debug(f"Added PR data to custom fields for {issue.key}")

            # Log all available custom fields for debugging
            all_custom_fields = []
            for field_name in dir(issue.fields):
                if field_name.startswith("customfield_"):
                    field_value = getattr(issue.fields, field_name, None)
                    if field_value is not None:
                        all_custom_fields.append(field_name)

            if all_custom_fields:
                logger.debug(f"Available custom fields for {issue.key}: {all_custom_fields}")

        except (AttributeError, Exception) as e:
            logger.debug(f"Could not extract custom fields from issue {issue.key}: {e}")

        # Create and return JiraIssueData object
        issue_data = JiraIssueData(
            key=details["key"],
            summary=details["summary"],
            description=details["description"],
            status=details["status"],
            priority=details["priority"],
            assignee=details["assignee"],
            reporter=details["reporter"],
            created_date=details["created_date"],
            updated_date=details["updated_date"],
            components=details["components"],
            labels=details["labels"],
            pull_requests=list(set(pr_urls)),  # Remove duplicates
            comments=comments_data if comments_data else None,
            custom_fields=custom_fields if custom_fields else None,
        )

        logger.debug(f"Finished formatting issue details for {issue.key}")
        logger.debug(f"Total unique PR URLs found for {issue.key}: {len(issue_data.pull_requests)}")

        return issue_data

    def get_issue(self, issue_key: str, include_all_comments: bool = True) -> str:
        """Retrieve detailed information about a Jira issue.

        Args:
            issue_key: The key of the issue to retrieve (e.g., PROJ-123)
            include_all_comments: Whether to fetch all comments (default: True)

        Returns:
            JSON string containing detailed issue information including GitHub PR links and all comments
        """
        try:
            logger.debug(f"Starting to retrieve issue {issue_key}")
            jira = self._get_jira_client()

            # Expand comments and changelog to get full issue data
            logger.debug(f"Fetching issue {issue_key} with comments and changelog expansion")
            issue = jira.issue(issue_key, expand="renderedFields,changelog,comments")

            logger.debug(f"Successfully fetched issue {issue_key}")

            # If we want all comments and the issue has comments, fetch them separately
            # This ensures we get all comments, not just the default limited set
            if include_all_comments and hasattr(issue.fields, "comment"):
                try:
                    logger.debug(f"Fetching all comments for {issue_key}")
                    all_comments = jira.comments(issue_key)
                    logger.debug(f"Retrieved {len(all_comments)} comments for {issue_key}")

                    # Replace the limited comments with all comments
                    issue.fields.comment.comments = all_comments
                    logger.debug(f"Updated issue with all {len(all_comments)} comments")
                except Exception as e:
                    logger.warning(f"Could not fetch all comments for {issue_key}: {e}")
                    # Continue with the comments we have from the original fetch

            issue_details = self._format_issue_details(issue)

            logger.debug(f"Retrieved issue details for {issue_key}")
            logger.debug(f"Found {len(issue_details.pull_requests)} PR URLs")
            logger.debug(f"Total comments processed: {len(issue_details.comments or [])}")

            return json.dumps(issue_details.model_dump(), indent=2)

        except Exception as e:
            error_msg = f"Error retrieving issue {issue_key}: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": str(e)})

    def search_issues(self, jql_query: str, max_results: int = 50) -> str:
        """Search for Jira issues using a JQL query.

        Args:
            jql_query: JQL query string to search for issues
            max_results: Maximum number of results to return (default: 50)

        Returns:
            JSON string containing list of matching issues
        """
        try:
            logger.debug(f"Starting search with JQL: {jql_query}")
            logger.debug(f"Max results: {max_results}")

            jira = self._get_jira_client()

            # Search with expanded fields for better data
            logger.debug("Executing JQL search with expanded fields")
            issues = jira.search_issues(jql_query, maxResults=max_results, expand="renderedFields,changelog")

            logger.debug(f"Found {len(issues)} issues matching the query")

            results = []
            for issue in issues:
                if not isinstance(issue, Issue):
                    logger.warning(f"Skipping non-Issue object: {issue}")
                    continue

                logger.debug(f"Processing issue {issue.key}")

                issue_details = {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                    "priority": issue.fields.priority.name if issue.fields.priority else "Unknown",
                    "created_date": str(issue.fields.created) if issue.fields.created else None,
                    "updated_date": str(issue.fields.updated) if issue.fields.updated else None,
                    "components": [comp.name for comp in issue.fields.components] if issue.fields.components else [],
                    "labels": list(issue.fields.labels) if issue.fields.labels else [],
                }

                # Add custom fields if they exist
                try:
                    custom_fields = {}

                    # Check for PR data
                    pr_data = getattr(issue.fields, "customfield_12310220", None)
                    if pr_data:
                        custom_fields["pr_data"] = pr_data
                        logger.debug(f"Found PR data in {issue.key}: {pr_data}")

                    # Check for release note text
                    release_note_text = getattr(issue.fields, "customfield_12317313", None)
                    if release_note_text:
                        custom_fields["release_note_text"] = release_note_text
                        logger.debug(f"Found release note text in {issue.key}")

                    # Check for release note status
                    release_note_status = getattr(issue.fields, "customfield_12310213", None)
                    if release_note_status:
                        if hasattr(release_note_status, "get"):
                            status_value = release_note_status.get("value")
                        else:
                            status_value = str(release_note_status)
                        custom_fields["release_note_status"] = status_value
                        logger.debug(f"Found release note status in {issue.key}: {status_value}")

                    if custom_fields:
                        issue_details["custom_fields"] = custom_fields

                except (AttributeError, Exception) as e:
                    logger.debug(f"Could not extract custom fields from {issue.key}: {e}")

                results.append(issue_details)

            logger.debug(f"Successfully processed {len(results)} issues for JQL '{jql_query}'")
            return json.dumps(results, indent=2)

        except Exception as e:
            error_msg = f"Error searching issues with JQL '{jql_query}': {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})

    def add_comment(self, issue_key: str, comment: str) -> str:
        """Add a comment to a Jira issue.

        Args:
            issue_key: The key of the issue to comment on
            comment: The comment text to add

        Returns:
            JSON string indicating success or error
        """
        try:
            logger.debug(f"Adding comment to issue {issue_key}")
            logger.debug(f"Comment text length: {len(comment)} characters")

            jira = self._get_jira_client()
            result = jira.add_comment(issue_key, comment)

            logger.info(f"Comment added to issue {issue_key}")
            logger.debug(f"Comment result: {result}")

            return json.dumps({"status": "success", "issue_key": issue_key, "message": "Comment added successfully"})

        except Exception as e:
            error_msg = f"Error adding comment to issue {issue_key}: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})

    def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        assignee: str | None = None,
        labels: list[str] | None = None,
    ) -> str:
        """Create a new Jira issue.

        Args:
            project_key: The key of the project to create the issue in
            summary: The summary/title of the issue
            description: The description of the issue
            issue_type: The type of issue (default: "Task")
            priority: The priority level (default: "Medium")
            assignee: Optional assignee username
            labels: Optional list of labels to add

        Returns:
            JSON string with the new issue's key and URL
        """
        try:
            logger.debug(f"Creating issue in project {project_key}")
            logger.debug(f"Issue type: {issue_type}, Priority: {priority}")
            logger.debug(f"Assignee: {assignee}, Labels: {labels}")
            logger.debug(f"Summary length: {len(summary)} characters")
            logger.debug(f"Description length: {len(description)} characters")

            jira = self._get_jira_client()

            # Build issue dictionary
            issue_dict = {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
            }

            # Add assignee if provided
            if assignee:
                issue_dict["assignee"] = {"name": assignee}
                logger.debug(f"Added assignee: {assignee}")

            # Add labels if provided
            if labels:
                issue_dict["labels"] = labels
                logger.debug(f"Added labels: {labels}")

            logger.debug(f"Issue dictionary: {issue_dict}")

            new_issue = jira.create_issue(fields=issue_dict)
            server_url = os.getenv("JIRA_URL", "")
            issue_url = f"{server_url}/browse/{new_issue.key}"

            logger.info(f"Issue created with key: {new_issue.key}")
            logger.debug(f"Issue URL: {issue_url}")

            return json.dumps(
                {
                    "key": new_issue.key,
                    "url": issue_url,
                    "status": "success",
                    "message": f"Issue {new_issue.key} created successfully",
                }
            )

        except Exception as e:
            error_msg = f"Error creating issue in project {project_key}: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
