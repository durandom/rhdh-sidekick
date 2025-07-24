"""
Jira Triager Agent for automatic team/component assignment.

This module implements an AI agent that analyzes previous support tickets and a current Jira ticket
and recommends the best-matching team and component for assignment.
"""

import uuid
from pathlib import Path
from typing import Any, Dict, Optional
import re

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from loguru import logger
from .jira_knowledge import JiraKnowledgeManager
from sidekick.utils.jira_client_utils import get_project_component_names

ALLOWED_TEAMS = [
    "RHIDP - Cope",
    "RHIDP - Documentation",
    "RHIDP - Dynamic Plugins",
    "RHIDP - Frontend Plugins & UI",
    "RHIDP - Install",
    "RHIDP - Management",
    "RHIDP - Performance and Scaling",
    "RHIDP - Plugin and AI",
    "RHIDP - Plugins",
    "RHIDP - Product Management",
    "RHIDP - Program Management",
    "RHIDP - RHTAP",
    "RHIDP - Security",
    "RHIDP - Support",
    "RHIDP - UXD",
    "RHOAI Workload Orchestration",
    "RHDHPAI - DevAI",
    "RHDHPAI - UI",
]

COMPONENT_TEAM_MAP = {
    "RHIDP - Plugins": [
        "3scale", "Actions", "Azure Container Registry plugin", "Bulk Import Plugin", "Matomo Analytics Provider Plugin",
        "Notifications plugin", "ocm", "Open Cluster Management plugin", "Platform plugins & Backend Plugins", "Plugins",
        "Quay Actions", "RBAC Plugin", "regex-actions", "Software Templates", "TechDocs", "Web Terminal plugin"
    ],
    "RHIDP - Frontend Plugins & UI": [
        "Bulk Import Plugin", "Frontend Plugins & UI", "Localization", "ocm", "Quickstart Plugin", "RBAC Plugin",
        "Theme", "Topology plugin", "UI"
    ],
    "RHIDP - Cope": [
        "Audit Log", "Build", "Catalog", "Core platform", "Event Module", "jfrog Artifactory", "Upstream"
    ],
    "RHIDP - Security": [
        "Authentication", "FIPs", "Keycloak provider", "Security"
    ],
    "RHIDP - Install": [
        "database", "Helm Chart", "Installation & Run", "Operator", "Orchestrator plugin", "RHDH Local"
    ],
    "RHIDP - UXD": [
        "Developer Hub UX"
    ],
    "RHIDP - Documentation": [
        "Documentation"
    ],
    "RHIDP - Dynamic Plugins": [
        "Dynamic plugins", "Marketplace"
    ],
    "RHIDP - RHTAP": [
        "ArgoCD Plugin", "Quay Plugin", "Tekton plugin"
    ],
    "RHIDP - Performance and Scaling": [
        "Performance"
    ],
    "RHDHPAI - DevAI": [
        "AI", "lightspeed"
    ],
    "RHIDP - Plugin and AI": [
        "AI"
    ],
    "RHDHPAI - UI": [
        "AI"
    ],
}

class JiraTriagerAgent:
    """
    AI agent for Jira ticket triage. Recommends the best team and component for a new Jira issue.
    Takes previous support ticket data and current issue fields as input.
    Uses RAG to find relevant historical tickets and passes them to the LLM.
    Only assigns missing fields, using existing assigned fields as context.

    CLI integration: If a Jira issue ID is provided, the CLI will fetch the issue fields automatically using get_jira_issue_fields.
    """

    def __init__(
        self,
        jira_knowledge_manager: JiraKnowledgeManager,
        storage_path: Optional[Path] = None,
        user_id: Optional[str] = None,
    ):
        """
        Initialize the Jira triager agent.

        Args:
            jira_knowledge_manager: JiraKnowledgeManager for RAG
            storage_path: Path for agent session storage
            user_id: Optional user ID for session management
        """
        if storage_path is None:
            storage_path = Path("tmp/jira_triager_agent.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self._agent: Optional[Agent] = None
        self._initialized = False
        self._session_id: Optional[str] = None
        self.jira_knowledge_manager = jira_knowledge_manager
        self.jira_knowledge_manager.load_issues(recreate=False)
        logger.debug(f"JiraTriagerAgent initialized: storage_path={storage_path}, user_id={user_id}")

    def _generate_session_id(self) -> str:
        """Generate a new session ID using UUID."""
        return str(uuid.uuid4())

    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new session for the agent.

        Args:
            user_id: Optional user ID to override the instance user_id

        Returns:
            The generated session ID
        """
        if user_id is not None:
            self.user_id = user_id
        self._session_id = self._generate_session_id()
        logger.debug(f"Created new session: session_id={self._session_id}, user_id={self.user_id}")
        return self._session_id

    def get_current_session(self) -> Optional[str]:
        """
        Get the current session ID.

        Returns:
            Current session ID or None if no session exists
        """
        return self._session_id

    def initialize(self) -> None:
        """
        Initialize the agent for triage, passing the knowledge base for RAG.
        """
        if self._initialized:
            logger.debug("Agent already initialized")
            return
        try:
            logger.debug("Initializing Jira triager agent")
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            storage = SqliteStorage(
                table_name="jira_triager_sessions",
                db_file=str(self.storage_path),
            )
            # Build a summary of the team-to-components mapping for the instructions
            team_component_lines = []
            for team, components in COMPONENT_TEAM_MAP.items():
                comps_str = ", ".join(sorted(components))
                team_component_lines.append(f"- {team}: {comps_str}")
            team_component_map_str = (
                "Team-to-Components Associations (not absolute, use as reference):\n"
                + "\n".join(team_component_lines)
            )
            self._agent = Agent(
                name="Jira Triager Agent",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are an expert Jira ticket triager.",
                    "Your job is to recommend the best team and component for a new Jira issue, based on previous support tickets.",
                    f"Only choose from the following teams: {', '.join(ALLOWED_TEAMS)}.",
                    "You will be given a list of previous tickets (with title, description, component, team) and the current ticket (title, description, component, team, assignee).",
                    "You will be provided with the allowed components for the current ticket in the prompt.",
                    team_component_map_str,
                    "Analyze the previous tickets for patterns and similarities to the current ticket.",
                    "Recommend the most likely team and component for the current ticket.",
                    "If the current ticket already has a component, team, or assignee, consider them when determining the best match.",
                    "Output ONLY a JSON object with keys 'team' and 'component'.",
                    "Do NOT include any explanation, markdown, or text outside the JSON.",
                    "Example: {\"team\": \"<team>\", \"component\": \"<component>\"}",
                ],
                tools=[],
                storage=storage,
                knowledge=self.jira_knowledge_manager._knowledge,
            )
            self._initialized = True
            logger.info("Jira triager agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jira triager agent: {e}")
            self._initialized = False
            raise RuntimeError(f"Agent initialization failed: {e}") from e

    def triage_ticket(
        self,
        current_ticket: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Recommend the missing team or component for a Jira ticket using RAG.

        Args:
            current_ticket: Dict with current ticket fields (title, description, component, team)
            session_id: Optional session ID to use for this triage

        Returns:
            Dict with only the missing field(s) assigned (e.g., {"team": ...} or {"component": ...} or both)
        """
        if not self._initialized:
            self.initialize()
        if self._agent is None:
            raise RuntimeError("Agent not properly initialized")
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()
        logger.debug(f"Triaging ticket with session_id={self._session_id}")

        # Determine which fields are missing (treat None and '' as missing)
        missing_fields = [
            field for field in ("team", "component")
            if current_ticket.get(field) is None or current_ticket.get(field) == ""
        ]

        if not missing_fields:
            logger.info("No fields to assign; both team and component are already set.")
            return {}

        # Build a focused prompt for the current ticket only
        component = current_ticket.get("component")
        project_key = current_ticket.get("project_key") or "RHIDP"
        allowed_components = get_project_component_names(project_key)

        prompt_lines = [f"Allowed components: {allowed_components}"]
        if component:
            prompt_lines.append(f"Current component: {component}")
        prompt_lines.extend([
            "Given the current Jira ticket (as JSON):",
            f"{current_ticket}",
            f"The current ticket is missing the following field(s): {missing_fields}.",
            "Use any assigned field(s (component, team, assignee)) as context to help determine the best match for the missing field(s).",
            "Recommend ONLY the missing field(s) as a JSON object (e.g., {\"team\": ...} or {\"component\": ...} or both).",
            "Do not include fields that are already assigned."
        ])
        prompt = "\n".join(prompt_lines)
        response = self._agent.run(prompt, stream=False, session_id=self._session_id, user_id=self.user_id)
        # Parse the response for the JSON object
        import json
        content = response.content if response.content is not None else '{}'
        # Remove Markdown code block markers if present
        clean_content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE | re.MULTILINE)
        try:
            result = json.loads(clean_content)
            # Only return the missing fields
            return {k: v for k, v in result.items() if k in missing_fields}
        except Exception as e:
            logger.error(f"Failed to parse agent response: {e}\nResponse: {response.content}")
            raise RuntimeError(f"Failed to parse agent response: {e}") from e
