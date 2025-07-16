"""
Test Analysis Agent with test failure analysis tools.

This module implements an AI agent that analyzes test failures from Playwright test runs
using the Agno framework with Google Cloud Storage and AI-powered analysis.
"""

import uuid
from pathlib import Path

from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from loguru import logger

from ..tools.test_analysis import (
    analyze_screenshot_visual_confirmation,
    get_failed_testsuites,
    get_folder_structure,
    get_immediate_log_files_content,
    get_test_analysis_prompt,
    get_text_from_file,
)


class TestAnalysisAgent:
    """AI-powered test failure analysis agent using Agno framework with test analysis tools."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
    ):
        """
        Initialize the test analysis agent.

        Args:
            storage_path: Path for agent session storage
            user_id: Optional user ID for session management
        """
        # Default storage path
        if storage_path is None:
            storage_path = Path("tmp/test_analysis_agent.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self._agent: Agent | None = None
        self._initialized = False
        self._session_id: str | None = None

        logger.debug(f"TestAnalysisAgent initialized: storage_path={storage_path}, user_id={user_id}")

    def _generate_session_id(self) -> str:
        """Generate a new session ID using UUID."""
        return str(uuid.uuid4())

    def create_session(self, user_id: str | None = None) -> str:
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

    def get_current_session(self) -> str | None:
        """
        Get the current session ID.

        Returns:
            Current session ID or None if no session exists
        """
        return self._session_id

    def initialize(self) -> None:
        """Initialize the agent with test analysis tools."""
        if self._initialized:
            logger.debug("Agent already initialized")
            return

        try:
            logger.info("Initializing test analysis agent")

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Create agent storage
            storage = SqliteStorage(
                table_name="test_analysis_sessions",
                db_file=str(self.storage_path),
            )

            # Initialize tools
            tools = [
                get_failed_testsuites,
                analyze_screenshot_visual_confirmation,
                get_text_from_file,
                get_folder_structure,
                get_immediate_log_files_content,
            ]

            # Create the agent
            self._agent = Agent(
                name="Test Analysis Expert",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are an AI expert in test automation analysis, specializing in Playwright test failures.",
                    "Your task is to analyze test failures from Prow CI logs and provide comprehensive "
                    "root cause analysis.",
                    "When given a prow link, extract the base directory and analyze the test artifacts systematically.",
                    "Always use the provided tools to gather information - do not assume content is pre-loaded.",
                    "Focus on analyzing:",
                    "- JUnit XML files for test failure details",
                    "- Screenshots for visual confirmation of failures",
                    "- Build logs for CI/deployment issues",
                    "- Pod logs for container-related problems",
                    "For each failed test case, provide:",
                    "1. Test Purpose: What the test was trying to verify",
                    "2. Failure Message: Exact error from JUnit XML",
                    "3. Root Cause Analysis: Detailed analysis using all available artifacts",
                    "4. Actionable Recommendations: Specific solutions (max 2)",
                    "For CI/Build failures, provide:",
                    "1. Issue Type: CI Failure/Build Failure/Pod Log Issue",
                    "2. Issue Description: Summary of the problem",
                    "3. Failure Details: Key error messages and symptoms",
                    "4. Root Cause Analysis: Analysis based on logs",
                    "5. Actionable Recommendations: Specific solutions (max 2)",
                    "Always be thorough in your analysis and use visual confirmation when screenshots are available.",
                    "Extract the GCS base directory from prow links in the format: logs/pull/123/test-run-456",
                    "Be systematic in your approach and don't skip any available artifacts.",
                ],
                tools=tools,
                storage=storage,
                add_datetime_to_instructions=True,
                add_history_to_messages=True,
                num_history_runs=3,
                markdown=True,
            )

            self._initialized = True
            logger.info("Test analysis agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize test analysis agent: {e}")
            self._initialized = False
            raise RuntimeError(f"Agent initialization failed: {e}") from e

    def analyze_test_failure(self, prow_link: str, session_id: str | None = None) -> RunResponse:
        """
        Analyze test failures from a Prow CI link.

        Args:
            prow_link: Prow CI link to analyze (e.g., https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456)
            session_id: Optional session ID to use for this analysis

        Returns:
            Agent response with test failure analysis
        """
        # Ensure agent is initialized
        if not self._initialized:
            self.initialize()

        if self._agent is None:
            raise RuntimeError("Agent not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.debug(f"Analyzing test failure from prow link: '{prow_link}' with session_id={self._session_id}")

        # Extract base directory from prow link
        import re

        pattern = r"https://prow\.ci\.openshift\.org/view/gs/test-platform-results/(logs/[^|>\s/]+(?:/[^|>\s/]+)*)"
        match = re.search(pattern, prow_link)

        if not match:
            return self._agent.run(
                f"Invalid prow link format: {prow_link}. Please provide a valid prow link in the format: https://prow.ci.openshift.org/view/gs/test-platform-results/logs/...",
                stream=False,
                session_id=self._session_id,
                user_id=self.user_id,
            )

        base_dir = match.group(1)
        logger.debug(f"Extracted base directory: {base_dir}")

        # Generate the comprehensive analysis prompt
        try:
            analysis_prompt = get_test_analysis_prompt(base_dir)
            logger.debug(f"Generated analysis prompt with {len(analysis_prompt)} characters")
        except Exception as e:
            logger.error(f"Failed to generate analysis prompt: {e}")
            analysis_prompt = f"""
Analyze test failures from the base directory: {base_dir}

Use the available tools to:
1. Get the folder structure to understand the layout
2. Find JUnit XML files and extract failed test suites
3. Analyze screenshots for visual confirmation
4. Review build logs and pod logs for CI issues

Provide a comprehensive analysis with root cause and actionable recommendations.
"""

        # Get response from agent
        response = self._agent.run(analysis_prompt, stream=False, session_id=self._session_id, user_id=self.user_id)

        return response

    def ask(self, query: str, session_id: str | None = None) -> RunResponse:
        """
        Ask a follow-up question or request modifications to the analysis.

        Args:
            query: Question or modification request
            session_id: Optional session ID to use for this query

        Returns:
            Agent response
        """
        # Ensure agent is initialized
        if not self._initialized:
            self.initialize()

        if self._agent is None:
            raise RuntimeError("Agent not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.debug(f"Processing ask query: '{query}' with session_id={self._session_id}")

        # Get response from agent
        response = self._agent.run(query, stream=False, session_id=self._session_id, user_id=self.user_id)

        return response
