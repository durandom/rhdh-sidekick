"""
Image Analysis Team for testing image accessibility between agents.

This module implements a coordinate mode team with two agents:
1. Image Analyzer - specializes in analyzing images
2. Text Analyzer - analyzes text content

The goal is to test when and how images are accessible to sub-agents.
"""

import uuid
from datetime import datetime
from pathlib import Path

from agno.agent import Agent
from agno.media import Image
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.team import Team
from agno.tools.file import FileTools
from loguru import logger


class ImageAnalysisTeam:
    """Coordinate mode team for testing image accessibility between agents."""

    def __init__(
        self,
        storage_path: Path | None = None,
        user_id: str | None = None,
        work_dir: Path | None = None,
    ):
        """
        Initialize the image analysis team.

        Args:
            storage_path: Path for team session storage
            user_id: Optional user ID for session management
            work_dir: Working directory for file operations
        """
        if storage_path is None:
            storage_path = Path("tmp/image_analysis_team.db")

        if work_dir is None:
            work_dir = Path("tmp/image_analysis_work")

        self.storage_path = storage_path
        self.user_id = user_id
        self.work_dir = work_dir
        self._team: Team | None = None
        self._initialized = False
        self._session_id: str | None = None

        logger.debug(
            f"ImageAnalysisTeam initialized: storage_path={storage_path}, user_id={user_id}, work_dir={work_dir}"
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

    def initialize(self) -> None:
        """Initialize the team with specialized agents."""
        if self._initialized:
            logger.debug("Team already initialized")
            return

        try:
            logger.info("Initializing image analysis team")

            # Create storage directory if needed
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.work_dir.mkdir(parents=True, exist_ok=True)

            # Create team storage
            storage = SqliteStorage(
                table_name="image_analysis_team_sessions",
                db_file=str(self.storage_path),
            )

            # Create image analysis agent
            image_agent = Agent(
                name="Image Analyzer",
                role="Analyzes images and provides detailed visual analysis",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are a specialist in analyzing images provided to the team.",
                    "Your role is to examine images and provide detailed visual analysis.",
                    "For each image you receive, analyze:",
                    "1. What objects, people, or elements are visible in the image",
                    "2. Colors, lighting, and composition",
                    "3. Any text or symbols visible in the image",
                    "4. The overall context and purpose of the image",
                    "5. Any notable features or anomalies",
                    "IMPORTANT: Always start your response by stating the current time and "
                    "whether you can see any images.",
                    "If you can see images, describe them in detail.",
                    "If you cannot see images, explicitly state that no images are available to you.",
                    "Be thorough and descriptive in your visual analysis.",
                ],
                tools=[FileTools(base_dir=self.work_dir)],
                add_datetime_to_instructions=True,
            )

            # Create text analysis agent
            text_agent = Agent(
                name="Text Analyzer",
                role="Analyzes text content and provides contextual analysis",
                model=Gemini(id="gemini-2.0-flash"),
                instructions=[
                    "You are a specialist in analyzing text content and providing contextual analysis.",
                    "Your role is to examine text provided to the team and provide insights.",
                    "For text analysis, focus on:",
                    "1. Key themes and topics in the text",
                    "2. Tone and sentiment",
                    "3. Important facts or data points",
                    "4. Structure and organization",
                    "5. Any questions or action items mentioned",
                    "IMPORTANT: Always start your response by stating the current time and "
                    "whether you can see any images.",
                    "If you can see images, describe what you see.",
                    "If you cannot see images, explicitly state that no images are available to you.",
                    "Focus primarily on text analysis but comment on image accessibility.",
                ],
                tools=[FileTools(base_dir=self.work_dir)],
                add_datetime_to_instructions=True,
            )

            # Create the coordinate mode team
            self._team = Team(
                name="Image Analysis Team",
                mode="coordinate",
                model=Gemini(id="gemini-2.0-flash"),
                members=[image_agent, text_agent],
                description="A team for testing image accessibility between agents",
                instructions=[
                    "You are the team leader coordinating analysis of content that may include images.",
                    "Your team has two specialists:",
                    "1. Image Analyzer - specializes in analyzing visual content",
                    "2. Text Analyzer - analyzes text content but also reports on image accessibility",
                    "Your coordination strategy:",
                    "1. First, note the current time and whether you can see any images yourself",
                    "2. Delegate to the Image Analyzer to analyze any visual content",
                    "3. Delegate to the Text Analyzer to analyze text content and report on image accessibility",
                    "4. Synthesize both responses to understand image accessibility patterns",
                    "IMPORTANT: Always start your response by stating:",
                    "- Current time",
                    "- Whether you (the team leader) can see any images",
                    "- How many images (if any) were provided to the team",
                    "Pay special attention to when and how images become accessible to different agents.",
                ],
                storage=storage,
                add_datetime_to_instructions=True,
                enable_agentic_context=True,
                share_member_interactions=True,
                show_members_responses=True,
                markdown=True,
            )

            self._initialized = True
            logger.info("Image analysis team initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize image analysis team: {e}")
            self._initialized = False
            raise RuntimeError(f"Team initialization failed: {e}") from e

    def analyze_with_image(self, text: str, image_path: str | None = None, session_id: str | None = None):
        """
        Analyze content with an optional image.

        Args:
            text: Text content to analyze
            image_path: Optional path to image file
            session_id: Optional session ID to use for this analysis

        Returns:
            Team response with analysis
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

        current_time = datetime.now().isoformat()
        logger.info(f"[{current_time}] Analyzing content with image: {image_path} and session_id={self._session_id}")

        # Prepare images if provided
        images = []
        if image_path:
            try:
                image = Image(filepath=image_path)
                images.append(image)
                logger.info(f"[{current_time}] Successfully created Image object from {image_path}")
            except Exception as e:
                logger.error(f"[{current_time}] Failed to create Image object from {image_path}: {e}")

        # Prepare the analysis request
        analysis_request = f"""
**Analysis Request at {current_time}**

Text to analyze: {text}

Image provided: {"Yes" if image_path else "No"}
Image path: {image_path if image_path else "None"}

**Task**: Analyze the provided content and report on image accessibility at each agent level.
Each agent should report:
1. Current time when they process the request
2. Whether they can see any images
3. If they can see images, describe what they see
4. Their primary analysis (text or image analysis)
"""

        # Get response from team with images
        response = self._team.run(
            analysis_request, images=images if images else None, session_id=self._session_id, user_id=self.user_id
        )

        logger.info(f"[{current_time}] Team analysis completed")
        return response

    def analyze_with_png_files(self, text: str, png_dir: str = "tmp", session_id: str | None = None):
        """
        Analyze content with PNG files found in the specified directory.

        Args:
            text: Text content to analyze
            png_dir: Directory to search for PNG files (default: "tmp")
            session_id: Optional session ID to use for this analysis

        Returns:
            Team response with analysis
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

        current_time = datetime.now().isoformat()
        logger.info(
            f"[{current_time}] Analyzing content with PNG files from {png_dir} and session_id={self._session_id}"
        )

        # Find all PNG files in the specified directory
        png_dir_path = Path(png_dir)
        png_files = list(png_dir_path.glob("*.png"))

        logger.info(f"[{current_time}] Found {len(png_files)} PNG files: {[f.name for f in png_files]}")

        # Prepare images from PNG files
        images = []
        image_info = []
        for png_file in png_files:
            try:
                image = Image(filepath=str(png_file))
                images.append(image)
                image_info.append(f"  - {png_file.name}")
                logger.info(f"[{current_time}] Successfully created Image object from {png_file}")
            except Exception as e:
                logger.error(f"[{current_time}] Failed to create Image object from {png_file}: {e}")
                image_info.append(f"  - {png_file.name} (FAILED: {e})")

        # Prepare the analysis request
        analysis_request = f"""
**Analysis Request at {current_time}**

Text to analyze: {text}

PNG files found in {png_dir}:
{chr(10).join(image_info)}

Images successfully loaded: {len(images)} out of {len(png_files)} PNG files

**Task**: Analyze the provided content and report on image accessibility at each agent level.
Each agent should report:
1. Current time when they process the request
2. Whether they can see any images
3. If they can see images, describe what they see (identify each image if possible)
4. How many images they can see
5. Their primary analysis (text or image analysis)

**Special focus**: Test image accessibility timing and distribution across agents.
"""

        # Get response from team with images
        response = self._team.run(
            analysis_request, images=images if images else None, session_id=self._session_id, user_id=self.user_id
        )

        logger.info(f"[{current_time}] Team analysis completed with {len(images)} images")
        return response

    def ask(self, query: str, session_id: str | None = None):
        """
        Ask a follow-up question.

        Args:
            query: Question or request
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

        current_time = datetime.now().isoformat()
        logger.debug(f"[{current_time}] Processing ask query: '{query}' with session_id={self._session_id}")

        # Get response from team
        response = self._team.run(query, session_id=self._session_id, user_id=self.user_id)

        return response


# Example usage and testing
if __name__ == "__main__":
    # Create team instance
    team = ImageAnalysisTeam(work_dir=Path("tmp/image_test_work"), user_id="test_user")

    # Test 1: Analysis without image
    print("=== Test 1: Analysis without image ===")
    response1 = team.analyze_with_image("Hello, this is a test message without an image.")
    print(f"Response: {response1.content}")
    print()

    # Test 2: Analysis with image (you would need to provide a real image path)
    print("=== Test 2: Analysis with image ===")
    # Uncomment and modify the path below to test with a real image
    # response2 = team.analyze_with_image("Please analyze this image.", "/path/to/your/image.jpg")
    # print(f"Response: {response2.content}")
    response2 = team.analyze_with_image("Please analyze this image.", None)  # No image for demo
    print(f"Response: {response2.content}")
    print()

    # Test 3: Follow-up question
    print("=== Test 3: Follow-up question ===")
    response3 = team.ask("Can you summarize what you learned about image accessibility?")
    print(f"Response: {response3.content}")
