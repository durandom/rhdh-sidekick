"""
Test Analysis Agent with pre-downloaded test artifacts.

This module implements an AI agent that analyzes test failures from Playwright test runs
using the Agno framework with pre-downloaded artifacts and AI-powered analysis.
"""

import uuid
from pathlib import Path
from typing import Any

from agno.agent import Agent, RunResponse
from agno.media import Image
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from loguru import logger

from ..utils.test_analysis import TestArtifactDownloader, extract_failed_testsuites


class TestAnalysisAgent:
    """AI-powered test failure analysis agent using pre-downloaded artifacts."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
        work_dir: Path | None = None,
    ):
        """
        Initialize the test analysis agent.

        Args:
            storage_path: Path for agent session storage
            user_id: Optional user ID for session management
            work_dir: Working directory for downloaded artifacts
        """
        # Default storage path
        if storage_path is None:
            storage_path = Path("tmp/test_analysis_agent.db")

        self.storage_path = storage_path
        self.user_id = user_id
        self.work_dir = work_dir
        self._agent: Agent | None = None
        self._initialized = False
        self._session_id: str | None = None

        logger.debug(
            f"TestAnalysisAgent initialized: storage_path={storage_path}, user_id={user_id}, work_dir={work_dir}"
        )

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
        """Initialize the agent without tools (uses pre-downloaded artifacts)."""
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

            # Create the agent without tools (uses pre-downloaded artifacts)
            self._agent = Agent(
                name="Test Analysis Expert",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are an AI expert in test automation analysis, specializing in Playwright test failures.",
                    "Your task is to analyze test failures from Prow CI logs and provide comprehensive "
                    "root cause analysis using pre-downloaded artifacts.",
                    "You will be provided with:",
                    "- JUnit XML content for test failure details",
                    "- Screenshots as images for visual confirmation of failures",
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
                    "When provided with screenshots, describe what you see and explain how it relates to the failure.",
                    "Be systematic in your approach and analyze all provided artifacts.",
                ],
                tools=[],  # No tools - uses pre-downloaded artifacts
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
        Analyze test failures from a Prow CI link by pre-downloading all artifacts.

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

        logger.info(f"Analyzing test failure from prow link: '{prow_link}' with session_id={self._session_id}")

        # Pre-download all artifacts using TestArtifactDownloader
        try:
            downloader = TestArtifactDownloader(prow_link, str(self.work_dir))
            artifacts = downloader.download_all_artifacts()
            logger.info(
                f"Downloaded artifacts: {len(artifacts['junit_files'])} JUnit files, "
                f"{len(artifacts['build_logs'])} build logs, "
                f"{len(artifacts['pod_logs'])} pod log sets"
            )

            # Generate analysis prompt with pre-downloaded content
            analysis_prompt = self._generate_analysis_prompt(prow_link, downloader.base_dir, artifacts)

            # Collect all images for the agent
            all_images: list[Image] = []
            if isinstance(artifacts["screenshots"], dict):
                for gcs_path, local_path in artifacts["screenshots"].items():
                    try:
                        image = Image(filepath=str(local_path))
                        all_images.append(image)
                        logger.info(f"Added screenshot for analysis: {gcs_path}")
                    except Exception as e:
                        logger.error(f"Failed to create Image object for {local_path}: {e}")

            logger.info(
                f"Running analysis with {len(all_images)} screenshots and {len(analysis_prompt)} character prompt"
            )

            # Get response from agent with images
            response = self._agent.run(
                analysis_prompt,
                # provide only the first image for initial analysis
                images=all_images[:1] if all_images else None,
                stream=False,
                session_id=self._session_id,
                user_id=self.user_id,
            )

            # Clean up downloaded files
            # downloader.cleanup()

            return response

        except Exception as e:
            logger.error(f"Failed to analyze test failure: {e}")
            return self._agent.run(
                f"Failed to analyze test failure from {prow_link}: {e}",
                stream=False,
                session_id=self._session_id,
                user_id=self.user_id,
            )

    def _generate_analysis_prompt(self, prow_link: str, base_dir: str, artifacts: dict[str, Any]) -> str:
        """Generate comprehensive analysis prompt with pre-downloaded content."""
        prompt_parts = []

        prompt_parts.append(f"""Test failure analysis for Prow link: {prow_link}
Base directory: {base_dir}

You are analyzing test failures with the following pre-downloaded artifacts:
""")

        # Add JUnit XML content
        if artifacts["junit_files"]:
            prompt_parts.append("\n## JUnit XML Test Results\n")
            for junit_name, junit_path in artifacts["junit_files"].items():
                try:
                    failed_testsuites = extract_failed_testsuites(junit_path)
                    prompt_parts.append(f"### {junit_name}\n```xml\n{failed_testsuites}\n```\n")
                except Exception as e:
                    prompt_parts.append(f"### {junit_name}\nError reading JUnit XML: {e}\n")

        # Add build logs
        if artifacts["build_logs"]:
            prompt_parts.append("\n## Build Logs\n")
            for log_name, log_path in artifacts["build_logs"].items():
                try:
                    with open(log_path) as f:
                        content = f.read()
                    prompt_parts.append(f"### {log_name}\n```\n{content}\n```\n")
                except Exception as e:
                    prompt_parts.append(f"### {log_name}\nError reading build log: {e}\n")

        # Add pod logs
        if artifacts["pod_logs"]:
            prompt_parts.append("\n## Pod Logs\n")
            for local_path in artifacts["pod_logs"].values():
                try:
                    with open(local_path) as f:
                        content = f.read()
                    prompt_parts.append(f"### {local_path.name}\n```\n{content}\n```\n")
                except Exception as e:
                    prompt_parts.append(f"### {local_path.name}\nError reading pod log: {e}\n")

        # Add screenshot information
        if artifacts["screenshots"]:
            prompt_parts.append("\n## Screenshots\n")
            screenshot_count = 0
            for gcs_path in artifacts["screenshots"]:
                screenshot_count += 1
                prompt_parts.append(f"- Screenshot {screenshot_count}: {gcs_path}\n")

            if screenshot_count > 0:
                prompt_parts.append(
                    f"\nNote: {screenshot_count} screenshots are provided as images for visual analysis.\n"
                )

        # Add failure information
        if artifacts["failed_downloads"]:
            prompt_parts.append("\n## Failed Downloads\n")
            prompt_parts.append("The following files could not be downloaded:\n")
            for failed_file in artifacts["failed_downloads"]:
                prompt_parts.append(f"- {failed_file}\n")

        prompt_parts.append("""
## Analysis Requirements

For each failed test case identified in the JUnit XML, provide:
1. **Test Case**: [Test Case Name]
2. **Test Purpose**: What the test was trying to verify
3. **Failure Message**: Exact error from JUnit XML
4. **Root Cause Analysis**: Based on all available artifacts including screenshots
5. **Actionable Recommendations**: Specific solutions (max 2)

For CI/Build failures, provide:
1. **Issue Type**: CI Failure/Build Failure/Pod Log Issue
2. **Issue Description**: Summary of the problem
3. **Failure Details**: Key error messages and symptoms
4. **Root Cause Analysis**: Analysis based on logs
5. **Actionable Recommendations**: Specific solutions (max 2)

When analyzing screenshots, describe what you see and explain how it relates to the failure.
Be systematic and thorough in your analysis.
""")

        return "".join(prompt_parts)

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
