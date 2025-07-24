"""
Tag Team with Jira and GitHub agents for collaborative ticket and PR management.

This module implements a coordinate mode team that combines Jira ticket management
with GitHub repository operations using specialized agents.
"""

import uuid
from pathlib import Path
from typing import Any

from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.team import Team, TeamRunResponse
from loguru import logger

from ..agents.github_agent import GitHubAgent
from ..agents.jira_agent import JiraAgent


def track_ticket_analysis(team: Team, ticket_key: str, summary: str) -> str:
    """Track a Jira ticket that has been analyzed in this session.

    Args:
        team: The team instance
        ticket_key: Jira ticket key (e.g., 'PROJ-123')
        summary: Brief summary of the ticket analysis
    """
    analyzed_tickets = team.team_session_state.get("analyzed_tickets", [])

    # Check if ticket is already tracked
    for ticket in analyzed_tickets:
        if ticket["key"] == ticket_key:
            ticket["summary"] = summary  # Update existing
            return f"Updated analysis tracking for {ticket_key}"

    # Add new ticket
    analyzed_tickets.append(
        {
            "key": ticket_key,
            "summary": summary,
            "timestamp": team.team_session_state.get("session_start_time", "unknown"),
        }
    )
    team.team_session_state["analyzed_tickets"] = analyzed_tickets

    return f"Now tracking analysis of {ticket_key}: {summary}"


def track_pr_analysis(team: Team, repo: str, pr_number: int, summary: str) -> str:
    """Track a GitHub PR that has been analyzed in this session.

    Args:
        team: The team instance
        repo: Repository name (e.g., 'owner/repo')
        pr_number: PR number
        summary: Brief summary of the PR analysis
    """
    analyzed_prs = team.team_session_state.get("analyzed_prs", [])

    pr_key = f"{repo}#{pr_number}"

    # Check if PR is already tracked
    for pr in analyzed_prs:
        if pr["key"] == pr_key:
            pr["summary"] = summary  # Update existing
            return f"Updated analysis tracking for {pr_key}"

    # Add new PR
    analyzed_prs.append(
        {
            "key": pr_key,
            "repo": repo,
            "number": pr_number,
            "summary": summary,
            "timestamp": team.team_session_state.get("session_start_time", "unknown"),
        }
    )
    team.team_session_state["analyzed_prs"] = analyzed_prs

    return f"Now tracking analysis of {pr_key}: {summary}"


def link_ticket_to_pr(team: Team, ticket_key: str, repo: str, pr_number: int, relationship: str = "implements") -> str:
    """Create a link between a Jira ticket and GitHub PR.

    Args:
        team: The team instance
        ticket_key: Jira ticket key
        repo: Repository name
        pr_number: PR number
        relationship: Type of relationship (implements, fixes, relates_to, etc.)
    """
    links = team.team_session_state.get("ticket_pr_links", {})
    pr_key = f"{repo}#{pr_number}"

    if ticket_key not in links:
        links[ticket_key] = []

    # Check if link already exists
    for link in links[ticket_key]:
        if link["pr_key"] == pr_key:
            link["relationship"] = relationship  # Update existing
            return f"Updated link: {ticket_key} {relationship} {pr_key}"

    # Add new link
    links[ticket_key].append({"pr_key": pr_key, "repo": repo, "pr_number": pr_number, "relationship": relationship})
    team.team_session_state["ticket_pr_links"] = links

    return f"Linked: {ticket_key} {relationship} {pr_key}"


def get_session_context(team: Team) -> str:
    """Get a summary of what has been analyzed and discovered in this session.

    Args:
        team: The team instance
    """
    context_parts = []

    # Session overview
    analyzed_tickets = team.team_session_state.get("analyzed_tickets", [])
    analyzed_prs = team.team_session_state.get("analyzed_prs", [])
    links = team.team_session_state.get("ticket_pr_links", {})
    current_focus = team.team_session_state.get("current_investigation", None)

    context_parts.append("## Session Context Summary")

    if current_focus:
        context_parts.append(f"**Current Focus:** {current_focus}")

    if analyzed_tickets:
        context_parts.append(f"**Analyzed Tickets ({len(analyzed_tickets)}):**")
        for ticket in analyzed_tickets[-5:]:  # Show last 5
            context_parts.append(f"- {ticket['key']}: {ticket['summary']}")

    if analyzed_prs:
        context_parts.append(f"**Analyzed PRs ({len(analyzed_prs)}):**")
        for pr in analyzed_prs[-5:]:  # Show last 5
            context_parts.append(f"- {pr['key']}: {pr['summary']}")

    if links:
        context_parts.append(f"**Discovered Links ({len(links)}):**")
        for ticket_key, pr_links in list(links.items())[:5]:  # Show first 5
            for link in pr_links:
                context_parts.append(f"- {ticket_key} {link['relationship']} {link['pr_key']}")

    if not any([analyzed_tickets, analyzed_prs, links]):
        context_parts.append("No tickets, PRs, or links have been analyzed yet in this session.")

    return "\n".join(context_parts)


def set_investigation_focus(team: Team, focus: str) -> str:
    """Set the current investigation focus for the team.

    Args:
        team: The team instance
        focus: Description of what we're currently investigating
    """
    team.team_session_state["current_investigation"] = focus
    return f"Set investigation focus: {focus}"


def update_user_preferences(team: Team, preference_key: str, preference_value: str) -> str:
    """Update user preferences for this session.

    Args:
        team: The team instance
        preference_key: Preference key (e.g., 'default_repo', 'search_filter')
        preference_value: Preference value
    """
    prefs = team.team_session_state.get("user_preferences", {})
    prefs[preference_key] = preference_value
    team.team_session_state["user_preferences"] = prefs

    return f"Updated preference {preference_key}: {preference_value}"


# Agent-level tools for accessing shared team state
def record_ticket_analysis(agent, ticket_key: str, summary: str) -> str:
    """Record that a Jira ticket has been analyzed (agent tool).

    Args:
        agent: The agent instance
        ticket_key: Jira ticket key (e.g., 'PROJ-123')
        summary: Brief summary of findings
    """
    if not hasattr(agent, "team_session_state") or agent.team_session_state is None:
        return "No team session state available"

    analyzed_tickets = agent.team_session_state.get("analyzed_tickets", [])

    # Check if ticket is already tracked
    for ticket in analyzed_tickets:
        if ticket["key"] == ticket_key:
            ticket["summary"] = summary
            return f"Updated analysis record for {ticket_key}"

    # Add new ticket
    analyzed_tickets.append({"key": ticket_key, "summary": summary, "analyzed_by": agent.name})
    agent.team_session_state["analyzed_tickets"] = analyzed_tickets

    return f"Recorded analysis of {ticket_key} by {agent.name}"


def record_pr_analysis(agent, repo: str, pr_number: int, summary: str) -> str:
    """Record that a GitHub PR has been analyzed (agent tool).

    Args:
        agent: The agent instance
        repo: Repository name (e.g., 'owner/repo')
        pr_number: PR number
        summary: Brief summary of findings
    """
    if not hasattr(agent, "team_session_state") or agent.team_session_state is None:
        return "No team session state available"

    analyzed_prs = agent.team_session_state.get("analyzed_prs", [])
    pr_key = f"{repo}#{pr_number}"

    # Check if PR is already tracked
    for pr in analyzed_prs:
        if pr["key"] == pr_key:
            pr["summary"] = summary
            return f"Updated analysis record for {pr_key}"

    # Add new PR
    analyzed_prs.append(
        {"key": pr_key, "repo": repo, "number": pr_number, "summary": summary, "analyzed_by": agent.name}
    )
    agent.team_session_state["analyzed_prs"] = analyzed_prs

    return f"Recorded analysis of {pr_key} by {agent.name}"


def create_ticket_pr_link(agent, ticket_key: str, repo: str, pr_number: int, relationship: str = "related") -> str:
    """Create a link between Jira ticket and GitHub PR (agent tool).

    Args:
        agent: The agent instance
        ticket_key: Jira ticket key
        repo: Repository name
        pr_number: PR number
        relationship: Type of relationship (implements, fixes, relates_to, etc.)
    """
    if not hasattr(agent, "team_session_state") or agent.team_session_state is None:
        return "No team session state available"

    links = agent.team_session_state.get("ticket_pr_links", {})
    pr_key = f"{repo}#{pr_number}"

    if ticket_key not in links:
        links[ticket_key] = []

    # Check if link already exists
    for link in links[ticket_key]:
        if link["pr_key"] == pr_key:
            link["relationship"] = relationship
            return f"Updated link: {ticket_key} {relationship} {pr_key}"

    # Add new link
    links[ticket_key].append(
        {
            "pr_key": pr_key,
            "repo": repo,
            "pr_number": pr_number,
            "relationship": relationship,
            "discovered_by": agent.name,
        }
    )
    agent.team_session_state["ticket_pr_links"] = links

    return f"Created link: {ticket_key} {relationship} {pr_key} (discovered by {agent.name})"


def get_analyzed_items(agent) -> str:
    """Get what has been analyzed so far in this session (agent tool).

    Args:
        agent: The agent instance
    """
    if not hasattr(agent, "team_session_state") or agent.team_session_state is None:
        return "No team session state available"

    analyzed_tickets = agent.team_session_state.get("analyzed_tickets", [])
    analyzed_prs = agent.team_session_state.get("analyzed_prs", [])
    links = agent.team_session_state.get("ticket_pr_links", {})

    result = []

    if analyzed_tickets:
        result.append(f"Analyzed Tickets: {', '.join([t['key'] for t in analyzed_tickets])}")

    if analyzed_prs:
        result.append(f"Analyzed PRs: {', '.join([p['key'] for p in analyzed_prs])}")

    if links:
        link_count = sum(len(pr_links) for pr_links in links.values())
        result.append(f"Discovered Links: {link_count} connections between tickets and PRs")

    return "; ".join(result) if result else "No items analyzed yet in this session"


class TagTeam:
    """Coordinate mode team for Jira and GitHub integration using specialized agents."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
        repository: str | None = None,
    ):
        """
        Initialize the tag team.

        Args:
            storage_path: Path for team session storage
            user_id: Optional user ID for session management
            repository: Default GitHub repository (format: "owner/repo")
        """
        if storage_path is None:
            storage_path = Path("tmp/tag_team.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self.repository = repository
        self._team: Team | None = None
        self._initialized = False
        self._session_id: str | None = None
        self._memory: Memory | None = None

        logger.debug(f"TagTeam initialized: storage_path={storage_path}, user_id={user_id}, repository={repository}")

    def _generate_session_id(self) -> str:
        """Generate a new session ID using UUID."""
        return str(uuid.uuid4())

    def create_session(self, user_id: str | None = None) -> str:
        """
        Create a new session for the team.

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

    def get_current_session(self) -> str | None:
        """
        Get the current session ID.

        Returns:
            Current session ID or None if no session exists
        """
        return self._session_id

    def clear_memory(self) -> None:
        """Clear the shared memory for all agents and team."""
        if self._memory is not None:
            self._memory.clear()
            logger.info("Cleared tag team memory")

    async def initialize(self) -> None:
        """Initialize the team with Jira and GitHub agents."""
        if self._initialized:
            logger.debug("Team already initialized")
            return

        try:
            logger.info("Initializing tag team")

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Create shared memory for persistent chat history
            self._memory = Memory()

            # Create team storage
            storage = SqliteStorage(
                table_name="tag_team_sessions",
                db_file=str(self.storage_path),
            )

            # Create Jira agent using the factory pattern
            jira_agent_factory = JiraAgent()
            mcp_tools = jira_agent_factory.create_mcp_tools()
            jira_agent = jira_agent_factory.create_agent(mcp_tools)

            # Update Jira agent for team coordination and add shared memory
            jira_agent.name = "Jira Specialist"
            jira_agent.role = "Manages Jira tickets, searches issues, and extracts ticket information"
            jira_agent.memory = self._memory  # Add shared memory for chat history
            # Add state-aware tools for tracking analysis
            jira_agent.tools.extend([record_ticket_analysis, create_ticket_pr_link, get_analyzed_items])
            # Get original instructions and add team coordination instructions
            original_instructions = jira_agent_factory.get_agent_instructions()
            team_instructions = [
                "When working with other team members:",
                "- Share relevant ticket information for GitHub operations",
                "- Connect Jira issues to GitHub PRs when requested",
                "- Provide context about business requirements from tickets",
                "- Use record_ticket_analysis to track tickets you analyze",
                "- Use create_ticket_pr_link when you discover connections to PRs",
                "- Use get_analyzed_items to see what has been analyzed previously",
                "Be concise but thorough in your responses to support team coordination.",
            ]
            jira_agent.instructions = original_instructions + team_instructions

            # Create GitHub agent using the factory pattern
            github_agent_factory = GitHubAgent(repository=self.repository)
            github_tools = github_agent_factory.create_github_tools()
            github_agent = github_agent_factory.create_agent(github_tools)

            # Update GitHub agent for team coordination and add shared memory
            github_agent.name = "GitHub Specialist"
            github_agent.role = "Manages GitHub repositories, pull requests, and code analysis"
            github_agent.memory = self._memory  # Add shared memory for chat history
            # Add state-aware tools for tracking analysis
            github_agent.tools.extend([record_pr_analysis, create_ticket_pr_link, get_analyzed_items])
            # Get original instructions and add team coordination instructions
            original_instructions = github_agent_factory.get_agent_instructions()
            team_instructions = [
                "When working with other team members:",
                "- Connect GitHub PRs to Jira tickets when requested",
                "- Provide technical context about code changes",
                "- Help identify relevant repositories for specific tasks",
                "- Use record_pr_analysis to track PRs you analyze",
                "- Use create_ticket_pr_link when you discover connections to tickets",
                "- Use get_analyzed_items to see what has been analyzed previously",
                "Be concise but thorough in your responses to support team coordination.",
            ]
            github_agent.instructions = original_instructions + team_instructions

            # Initialize team session state for shared context tracking
            from datetime import datetime

            team_session_state: dict[str, Any] = {
                "analyzed_tickets": [],
                "analyzed_prs": [],
                "ticket_pr_links": {},
                "current_investigation": None,
                "user_preferences": {},
                "session_start_time": datetime.now().isoformat(),
            }

            # Team's private session state for metrics and coordination
            team_private_state: dict[str, Any] = {
                "coordination_actions": [],
                "specialist_interactions": 0,
                "session_metrics": {},
            }

            # Create the coordinate mode team
            self._team = Team(
                name="Tag Team",
                mode="coordinate",
                model=Gemini(id="gemini-2.5-flash"),
                members=[jira_agent, github_agent],
                description=(
                    "A specialized team for coordinating Jira ticket management with GitHub repository operations"
                ),
                instructions=[
                    "You are the team leader coordinating between Jira and GitHub operations.",
                    "Your team consists of two specialists:",
                    "1. Jira Specialist - handles ticket management, searches, and analysis",
                    "2. GitHub Specialist - handles repository operations, PR analysis, and code review",
                    "Your coordination strategy:",
                    "1. Analyze user requests to determine which specialists are needed",
                    "2. For ticket-related queries, delegate to the Jira Specialist first",
                    "3. For repository or PR queries, delegate to the GitHub Specialist",
                    "4. For cross-platform tasks (linking tickets to PRs), coordinate both specialists",
                    "5. Synthesize responses from both specialists into coherent answers",
                    "Common coordination patterns:",
                    "- Ticket analysis: Get ticket details from Jira, then find related PRs in GitHub",
                    "- PR review: Get PR details from GitHub, then check for linked Jira tickets",
                    "- Feature tracking: Connect Jira feature tickets to GitHub implementation PRs",
                    "- Bug investigation: Link Jira bug reports to GitHub fixes and code changes",
                    "Available team management tools:",
                    "- get_session_context: See what has been analyzed in this session",
                    "- set_investigation_focus: Set current investigation focus",
                    "- track_ticket_analysis/track_pr_analysis: Track analysis progress",
                    "- link_ticket_to_pr: Create explicit links between tickets and PRs",
                    "Always provide clear, actionable responses that leverage insights from both platforms.",
                    "When information is requested from both platforms, ensure responses are well-integrated.",
                    "You have access to the conversation history and shared session state.",
                    "Use the session context to avoid redundant analysis and build on previous work.",
                ],
                tools=[
                    get_session_context,
                    set_investigation_focus,
                    track_ticket_analysis,
                    track_pr_analysis,
                    link_ticket_to_pr,
                    update_user_preferences,
                ],
                team_session_state=team_session_state,  # Shared state for all team members
                session_state=team_private_state,  # Team leader's private state
                storage=storage,
                memory=self._memory,  # Add shared memory for persistent chat history
                add_datetime_to_instructions=True,
                enable_agentic_context=True,
                enable_team_history=True,  # Enable chat history within sessions
                share_member_interactions=True,
                show_members_responses=True,
                markdown=True,
            )

            self._initialized = True
            logger.info("Tag team initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize tag team: {e}")
            self._initialized = False
            raise RuntimeError(f"Team initialization failed: {e}") from e

    async def run(self, query: str, session_id: str | None = None) -> TeamRunResponse:
        """
        Run a query against the tag team.

        Args:
            query: Question or task for the team
            session_id: Optional session ID to use for this query

        Returns:
            Team response with coordinated analysis
        """
        if not self._initialized:
            await self.initialize()

        if self._team is None:
            raise RuntimeError("Team not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.info(f"Processing query: '{query}' with session_id={self._session_id}")

        # Get response from team
        response = self._team.run(query, session_id=self._session_id, user_id=self.user_id)

        return response

    async def acli_app(
        self,
        message: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        user: str = "User",
        emoji: str = ":label:",
        stream: bool = False,
        markdown: bool = False,
        exit_on: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Run an interactive command-line interface to interact with the tag team.
        Works with team dependencies requiring async logic.

        Args:
            message: Initial message to send
            session_id: Optional session ID to use
            user_id: Optional user ID for session management
            user: User identifier for display
            emoji: Emoji to use in prompts
            stream: Whether to stream responses
            markdown: Whether to render markdown
            exit_on: List of exit commands
            **kwargs: Additional arguments
        """
        from rich.prompt import Prompt

        if not self._initialized:
            await self.initialize()

        if self._team is None:
            raise RuntimeError("Team not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session(user_id)

        # Use provided user_id or keep existing
        if user_id is not None:
            self.user_id = user_id

        if message:
            await self.aprint_response(
                message=message, stream=stream, markdown=markdown, session_id=self._session_id, **kwargs
            )

        _exit_on = exit_on or ["exit", "quit", "bye"]
        while True:
            message = Prompt.ask(f"[bold] {emoji} {user} [/bold]")
            if message in _exit_on:
                break

            await self.aprint_response(
                message=message, stream=stream, markdown=markdown, session_id=self._session_id, **kwargs
            )

    async def aprint_response(
        self,
        message: str,
        stream: bool = False,
        markdown: bool = False,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Print the team's response to a message with proper formatting.
        Uses the Team's built-in aprint_response method.

        Args:
            message: The message to send to the team
            stream: Whether to stream the response
            markdown: Whether to render markdown
            session_id: Optional session ID to use
            **kwargs: Additional arguments
        """
        if self._team is None:
            raise RuntimeError("Team not properly initialized")

        # Use the team's built-in aprint_response method which handles formatting
        await self._team.aprint_response(
            message=message,
            stream=stream,
            markdown=markdown,
            session_id=session_id or self._session_id,
            user_id=self.user_id,
            **kwargs,
        )
