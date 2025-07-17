"""
Test Analysis Team with specialized agents for screenshot and log analysis.

This module implements a coordinate mode team that analyzes test failures using
specialized agents for different types of artifacts.
"""

import uuid
from pathlib import Path
from typing import Any

from agno.agent import Agent
from agno.media import Image
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.team import Team, TeamRunResponse
from agno.tools.file import FileTools
from loguru import logger

from ..utils.test_analysis import TestArtifactDownloader, extract_failed_testsuites


class TestAnalysisTeam:
    """Coordinate mode team for test failure analysis using specialized agents."""

    def __init__(
        self,
        prow_link: str,
        storage_path: Path | None = None,
        user_id: str | None = None,
        work_dir: Path | None = None,
    ):
        """
        Initialize the test analysis team.

        Args:
            prow_link: Prow CI link to analyze
            storage_path: Path for team session storage
            user_id: Optional user ID for session management
            work_dir: Working directory for downloaded artifacts
        """
        if storage_path is None:
            storage_path = Path("tmp/test_analysis_team.db")

        self.prow_link = prow_link
        self.storage_path = storage_path
        self.user_id = user_id
        self.work_dir = work_dir
        self._team: Team | None = None
        self._initialized = False
        self._session_id: str | None = None
        self._downloader: TestArtifactDownloader | None = None

        logger.debug(
            f"TestAnalysisTeam initialized: storage_path={storage_path}, user_id={user_id}, work_dir={work_dir}"
        )

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

    def initialize(self) -> None:
        """Initialize the team with specialized agents."""
        if self._initialized:
            logger.debug("Team already initialized")
            return

        try:
            logger.info("Initializing test analysis team")

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Create downloader with the prow_link
            self._downloader = TestArtifactDownloader(self.prow_link, str(self.work_dir))
            file_tools_base_dir = Path(self._downloader.work_dir)

            # Create team storage
            storage = SqliteStorage(
                table_name="test_analysis_team_sessions",
                db_file=str(self.storage_path),
            )

            # Create screenshot analysis agent
            Agent(
                name="Screenshot Analyzer",
                role="Analyzes test failure screenshots for visual confirmation",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are a specialist in analyzing test failure screenshots from Playwright tests.",
                    "Your role is to examine screenshots and provide detailed visual analysis of test failures.",
                    "For each screenshot provided, analyze:",
                    "1. What is visible in the screenshot",
                    "2. Any error messages or UI anomalies visible",
                    "3. Expected vs actual state of the UI",
                    "4. Visual clues about the failure cause",
                    "5. How the visual evidence relates to the test failure",
                    "Be thorough and descriptive in your visual analysis.",
                    "Focus on actionable insights that can help diagnose the root cause.",
                ],
                tools=[FileTools(base_dir=file_tools_base_dir)],
                add_datetime_to_instructions=True,
            )

            # Create log analysis agent
            log_agent = Agent(
                name="Log Analyzer",
                role="Analyzes build logs, pod logs, and JUnit XML for failure patterns",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are a specialist in analyzing CI/CD logs and test output files.",
                    "Your role is to examine build logs, pod logs, and JUnit XML files for failure patterns.",
                    "For log analysis, focus on:",
                    "1. Error messages and stack traces",
                    "2. Timing issues and timeouts",
                    "3. Resource constraints or deployment issues",
                    "4. Configuration problems",
                    "5. Dependency or environment issues",
                    "For JUnit XML analysis, extract:",
                    "1. Failed test case names and error messages",
                    "2. Test execution patterns and timing",
                    "3. Failure categories and frequencies",
                    "Provide systematic analysis with specific error details and root cause insights.",
                    "Use file tools to read and analyze log files as needed.",
                ],
                tools=[FileTools(base_dir=file_tools_base_dir)],
                add_datetime_to_instructions=True,
            )

            # Create the coordinate mode team
            self._team = Team(
                name="Test Analysis Team",
                mode="coordinate",
                model=Gemini(id="gemini-2.0-flash"),
                # members=[screenshot_agent, log_agent],
                members=[log_agent],
                description="A specialized team for analyzing test failures using visual and log analysis",
                instructions=[
                    "You are the team leader coordinating analysis of test failures from Prow CI.",
                    "Your team has two specialists:",
                    "1. Screenshot Analyzer - analyzes visual evidence from test failure screenshots",
                    "2. Log Analyzer - analyzes build logs, pod logs, and JUnit XML files",
                    "Your coordination strategy:",
                    "1. First, delegate log analysis to extract failure summary and patterns",
                    "2. Then, delegate screenshot analysis for visual confirmation and additional insights",
                    "3. Synthesize both analyses into comprehensive failure analysis",
                    "4. Provide actionable recommendations based on combined findings",
                    "For each failed test case, ensure the final analysis includes:",
                    "- Test Purpose: What the test was trying to verify",
                    "- Failure Message: Exact error from logs/JUnit XML",
                    "- Root Cause Analysis: Based on both visual and log evidence",
                    "- Actionable Recommendations: Specific solutions (max 2 per failure)",
                    "For CI/Build failures, provide:",
                    "- Issue Type: CI Failure/Build Failure/Pod Log Issue",
                    "- Issue Description: Summary of the problem",
                    "- Failure Details: Key error messages and symptoms",
                    "- Root Cause Analysis: Analysis based on logs",
                    "- Actionable Recommendations: Specific solutions (max 2)",
                    "Always synthesize insights from both team members into a cohesive analysis.",
                ],
                storage=storage,
                add_datetime_to_instructions=True,
                enable_agentic_context=True,
                share_member_interactions=True,
                show_members_responses=True,
                markdown=True,
            )

            self._initialized = True
            logger.info("Test analysis team initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize test analysis team: {e}")
            self._initialized = False
            raise RuntimeError(f"Team initialization failed: {e}") from e

    def analyze_test_failure(self, session_id: str | None = None) -> TeamRunResponse:
        """
        Analyze test failures from a Prow CI link using the coordinated team.

        Args:
            session_id: Optional session ID to use for this analysis

        Returns:
            Team response with coordinated test failure analysis
        """
        if not self._initialized:
            self.initialize()

        if self._team is None:
            raise RuntimeError("Team not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.info(f"Analyzing test failure from prow link: '{self.prow_link}' with session_id={self._session_id}")

        # Pre-download all artifacts
        # Use the downloader created during initialization
        if self._downloader is None:
            raise RuntimeError("Downloader not initialized")
        artifacts = self._downloader.download_all_artifacts()
        logger.info(
            f"Downloaded artifacts: {len(artifacts['junit_files'])} JUnit files, "
            f"{len(artifacts['build_logs'])} build logs, "
            f"{len(artifacts['pod_logs'])} pod log sets"
        )

        # Generate failure summary for team coordination
        failure_summary = self._generate_failure_summary(artifacts)

        # Collect only one image for the team
        all_images: list[Image] = []
        # if artifacts['screenshots']:
        #     first_screenshot_path = next(iter(artifacts['screenshots'].values()))
        #     first_screenshot_gcs = next(iter(artifacts['screenshots'].keys()))
        #     try:
        #         image = Image(filepath=str(first_screenshot_path))
        #         all_images.append(image)
        #         logger.info(f"Added single screenshot for analysis: {first_screenshot_gcs}")
        #     except Exception as e:
        #         logger.error(f"Failed to create Image object for {first_screenshot_path}: {e}")

        # logger.info(f"Running team analysis with {len(all_images)} screenshot "
        #             f"and {len(failure_summary)} character summary")

        # Get response from team with images
        response = self._team.run(
            failure_summary,
            images=all_images if all_images else None,
            session_id=self._session_id,
            user_id=self.user_id,
        )

        # Clean up downloaded files
        # downloader.cleanup()

        return response

    def _generate_failure_summary(self, artifacts: dict[str, Any]) -> str:
        """Generate a simplified failure summary with only one failing test case and one image."""
        summary_parts = []

        summary_parts.append(f"""Test failure analysis for Prow link: {self.prow_link}

## Task Overview
Analyze test failures using the downloaded artifacts. Focus on one representative failure.

## Available Artifacts
""")

        # Include only one failing JUnit test case
        if artifacts["junit_files"]:
            summary_parts.append(f"- **JUnit XML files**: {len(artifacts['junit_files'])} files")
            for junit_name, junit_path in artifacts["junit_files"].items():
                try:
                    failed_testsuites = extract_failed_testsuites(junit_path)
                    if failed_testsuites.strip():
                        import xml.etree.ElementTree as ET

                        root = ET.fromstring(failed_testsuites)
                        for testcase in root.iter("testcase"):
                            if testcase.find("failure") is not None or testcase.find("error") is not None:
                                test_name = testcase.get("name", "Unknown")
                                summary_parts.append(f"\n**Sample Failed Test**: {junit_name}: {test_name}")
                except Exception as e:
                    summary_parts.append(f"\n**JUnit Error**: {junit_name}: Error reading file - {e}")
                    break

        # if artifacts['screenshots']:
        #     first_screenshot = next(iter(artifacts['screenshots'].keys()))
        #     summary_parts.append(f"\n- **Screenshot**: 1 image provided for visual analysis")
        #     summary_parts.append(f"  - {first_screenshot}")

        summary_parts.append("""

## Analysis Instructions
1. **Log Analyzer**: Read and analyze the JUnit XML files for the specific failed test
2. **Screenshot Analyzer**: Examine the provided screenshot for visual evidence
3. **Team Leader**: Synthesize both analyses into focused failure analysis

The artifact files are available in the working directory for detailed analysis.
""")

        return "".join(summary_parts)

    def ask(self, query: str, session_id: str | None = None) -> TeamRunResponse:
        """
        Ask a follow-up question or request modifications to the analysis.

        Args:
            query: Question or modification request
            session_id: Optional session ID to use for this query

        Returns:
            Team response
        """
        if not self._initialized:
            self.initialize()

        if self._team is None:
            raise RuntimeError("Team not properly initialized")

        # Use provided session_id or create new session if none exists
        if session_id is not None:
            self._session_id = session_id
        elif self._session_id is None:
            self.create_session()

        logger.debug(f"Processing ask query: '{query}' with session_id={self._session_id}")

        # Get response from team
        response = self._team.run(query, session_id=self._session_id, user_id=self.user_id)

        return response
