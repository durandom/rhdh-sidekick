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

ALLOWED_TEAMS = [
    "RHDHPAI - DevAI",
    "RHDHPAI - UI",
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
    "RHIDP - QE",
    "RHIDP - RHTAP",
    "RHIDP - Security",
    "RHIDP - Support",
    "RHIDP - UXD",
    "RHOAI Workload Orchestration",
]

ALLOWED_COMPONENTS = [
    # RHIDP - Cope
    "build/release",
    "core platform",
    "backstage version adoption",
    "Logging",
    "upstream",
    "community advocacy & support",
    #RHIDP - Install
    "helm chart",
    "Operator",
    "Corporate proxy",
    "External database",
    "RHDH Local",
    # RHIDP - Security
    "authentication",
    "auth providers",
    "Security",
    "CVEs",
    # RHIDP - Plugins
    "plugins",
    "Gitlab",
    "azure plugin",
    "bulk import",
    "open cluster management",
    "rbac plugin",
    "web terminal plugin",
    "techdocs plugin",
    "software templates",
    "Actions",
    "Notification",
    "3scale",
    "regex-action",
    "quay-action",
    # RHIDP - Dynamic Plugins
    "dynamic plugin tooling",
    "Marketplace",
    # RHIDP - Frontend Plugins & UI
    "UI",
    "Bulk import plugin",
    "Topology Plugin",
    # RHIDP - Documentation
    "Documentation",
    "UXD",
    # RHDHPAI - UI
    "rhdh-plugins",
    "lightspeed",
    "Insights",
]

COMPONENT_TEAM_MAP = {
    # RHIDP - Cope
    "build/release": "RHIDP - Cope",
    "core platform": "RHIDP - Cope",
    "backstage version adoption": "RHIDP - Cope",
    "Logging": "RHIDP - Cope",
    "upstream": "RHIDP - Cope",
    "community advocacy & support": "RHIDP - Cope",
    # RHIDP - Install
    "helm chart": "RHIDP - Install",
    "Operator": "RHIDP - Install",
    "Corporate proxy": "RHIDP - Install",
    "External database": "RHIDP - Install",
    "RHDH Local": "RHIDP - Install",
    # RHIDP - Security
    "authentication": "RHIDP - Security",
    "auth providers": "RHIDP - Security",
    "Security": "RHIDP - Security",
    "CVEs": "RHIDP - Security",
    # RHIDP - Plugins
    "plugins": "RHIDP - Plugins",
    "Gitlab": "RHIDP - Plugins",
    "azure plugin": "RHIDP - Plugins",
    "bulk import": "RHIDP - Plugins",
    "open cluster management": "RHIDP - Plugins",
    "rbac plugin": "RHIDP - Plugins",
    "web terminal plugin": "RHIDP - Plugins",
    "techdocs plugin": "RHIDP - Plugins",
    "software templates": "RHIDP - Plugins",
    "Actions": "RHIDP - Plugins",
    "Notification": "RHIDP - Plugins",
    "3scale": "RHIDP - Plugins",
    "regex-action": "RHIDP - Plugins",
    "quay-action": "RHIDP - Plugins",
    # RHIDP - Dynamic Plugins
    "dynamic plugin tooling": "RHIDP - Dynamic Plugins",
    "Marketplace": "RHIDP - Dynamic Plugins",
    # RHIDP - Frontend Plugins & UI
    "UI": "RHIDP - Frontend Plugins & UI",
    "Bulk import plugin": "RHIDP - Frontend Plugins & UI",
    "Topology Plugin": "RHIDP - Frontend Plugins & UI",
    # RHIDP - Documentation
    "Documentation": "RHIDP - Documentation",
    "UXD": "RHIDP - Documentation",
    # RHDHPAI - UI
    "rhdh-plugins": "RHDHPAI - UI",
    "lightspeed": "RHDHPAI - UI",
    "Insights": "RHDHPAI - UI",
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
        logger.info(f"Created new session: session_id={self._session_id}, user_id={self.user_id}")
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
            logger.info("Initializing Jira triager agent")
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            storage = SqliteStorage(
                table_name="jira_triager_sessions",
                db_file=str(self.storage_path),
            )
            self._agent = Agent(
                name="Jira Triager Agent",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are an expert Jira ticket triager.",
                    "Your job is to recommend the best team and component for a new Jira issue, based on previous support tickets.",
                    f"Only choose from the following teams: {', '.join(ALLOWED_TEAMS)}.",
                    f"Only choose from the following components: {', '.join(ALLOWED_COMPONENTS)}.",
                    "You will be given a list of previous tickets (with title, description, component, team, assignee) and the current ticket (title, description, component, team, assignee).",
                    "Analyze the previous tickets for patterns and similarities to the current ticket.",
                    "Recommend the most likely team and component for the current ticket.",
                    "If the current ticket already has a component, team, or assignee, consider them when determining the best match, but override if a better match is found.",
                    "Output ONLY a JSON object with keys 'team' and 'component'.",
                    "Do NOT include any explanation, markdown, or text outside the JSON.",
                    "Example: {\"team\": \"RHIDP - Security\", \"component\": \"authentication\"}",
                ],
                tools=[],
                storage=storage,
                knowledge=self.jira_knowledge_manager._knowledge,
                add_datetime_to_instructions=True,
                add_history_to_messages=True,
                num_history_runs=3,
                markdown=True,
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

        # Determine which fields are missing
        missing_fields = []
        if not current_ticket.get("team"):
            missing_fields.append("team")
        if not current_ticket.get("component"):
            missing_fields.append("component")

        if not missing_fields:
            logger.info("No fields to assign; both team and component are already set.")
            return {}

        # Build a focused prompt for the current ticket only
        component = current_ticket.get("component")
        suggested_team = COMPONENT_TEAM_MAP.get(component)
        prompt_lines = [
            f"Allowed teams: {ALLOWED_TEAMS}",
            f"Allowed components: {ALLOWED_COMPONENTS}",
        ]
        if component and suggested_team:
            prompt_lines.append(f"For the component '{component}', the usual owning team is '{suggested_team}'. However, use your judgment based on the ticket context.")
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
