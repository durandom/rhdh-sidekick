"""
Test analysis tools for the sidekick CLI application.

This module provides test failure analysis tools using the @tool decorator
for use with AI agents in the sidekick application.
"""

import xml.etree.ElementTree as ET

from agno.tools import tool
from google.cloud import storage
from loguru import logger


class GCSStorageClient:
    """Google Cloud Storage client for test artifact access."""

    def __init__(self, bucket_name: str = "test-platform-results"):
        """Initialize GCS client with bucket name."""
        self.bucket_name = bucket_name
        self._client = None
        self._bucket = None
        logger.debug(f"GCS client configured for bucket: {bucket_name}")

    @property
    def client(self):
        """Lazy initialize GCS client."""
        if self._client is None:
            # Use anonymous client for public buckets
            self._client = storage.Client.create_anonymous_client()
            logger.debug("Initialized anonymous GCS client for public bucket")
        return self._client

    @property
    def bucket(self):
        """Lazy initialize GCS bucket."""
        if self._bucket is None:
            self._bucket = self.client.bucket(self.bucket_name)
            logger.debug(f"Initialized GCS bucket: {self.bucket_name}")
        return self._bucket

    def get_text_from_blob(self, blob_path: str) -> str:
        """Get text content from a blob."""
        try:
            blob = self.bucket.blob(blob_path)
            content = blob.download_as_text()
            logger.debug(f"Retrieved text from blob: {blob_path} ({len(content)} chars)")
            return str(content)
        except Exception as e:
            logger.error(f"Error reading blob {blob_path}: {e}")
            raise

    def get_bytes_from_blob(self, blob_path: str) -> bytes:
        """Get bytes content from a blob."""
        try:
            blob = self.bucket.blob(blob_path)
            content = blob.download_as_bytes()
            logger.debug(f"Retrieved bytes from blob: {blob_path} ({len(content)} bytes)")
            return bytes(content)
        except Exception as e:
            logger.error(f"Error reading blob {blob_path}: {e}")
            raise

    def blob_exists(self, blob_path: str) -> bool:
        """Check if a blob exists."""
        try:
            blob = self.bucket.blob(blob_path)
            exists = blob.exists()
            logger.debug(f"Blob exists check for {blob_path}: {exists}")
            return bool(exists)
        except Exception as e:
            logger.debug(f"Error checking blob existence {blob_path}: {e}")
            return False

    def list_blobs(self, prefix: str) -> list[str]:
        """List all blobs with given prefix."""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            blob_names = [blob.name for blob in blobs]
            logger.debug(f"Listed {len(blob_names)} blobs with prefix: {prefix}")
            return blob_names
        except Exception as e:
            logger.error(f"Error listing blobs with prefix {prefix}: {e}")
            raise

    def get_immediate_files(self, prefix: str) -> list[str]:
        """Get immediate files (not directories) from prefix."""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix, delimiter="/")
            # Get just the filenames, not full paths
            files = []
            for blob in blobs:
                if blob.name != prefix and not blob.name.endswith("/"):
                    # Extract just the filename from the full path
                    filename = blob.name.split("/")[-1]
                    files.append(filename)
            logger.debug(f"Found {len(files)} immediate files in {prefix}")
            return files
        except Exception as e:
            logger.error(f"Error getting immediate files from {prefix}: {e}")
            raise

    def get_immediate_directories(self, prefix: str) -> list[str]:
        """Get immediate directories from prefix."""
        try:
            dirs = set()
            for blob in self.bucket.list_blobs(prefix=prefix):
                # Get the part after the prefix
                relative_path = blob.name[len(prefix) :]
                # Only get the first directory name (before any slash)
                if relative_path and "/" in relative_path:
                    dir_name = relative_path.split("/")[0]
                    dirs.add(dir_name)

            directories = sorted(list(dirs))
            logger.debug(f"Found {len(directories)} immediate directories in {prefix}: {directories}")
            return directories
        except Exception as e:
            logger.error(f"Error getting immediate directories from {prefix}: {e}")
            # Return empty list instead of raising to allow graceful degradation
            return []


# Global storage client instance
storage_client = GCSStorageClient()


@tool(
    name="get_failed_testsuites",
    description="Extract failed test suites from JUnit XML file",
    show_result=True,
    cache_results=True,
    cache_ttl=300,  # 5 minutes cache
)
def get_failed_testsuites(xml_file_path: str) -> str:
    """
    Get test suites from JUnit XML with failures.

    Args:
        xml_file_path: Path to XML file in GCS

    Returns:
        XML string of failed testsuites
    """
    try:
        logger.debug(f"Getting failed testsuites from: {xml_file_path}")

        # Get XML content from GCS
        xml_content = storage_client.get_text_from_blob(xml_file_path)

        # Check if the file has been sanitized/removed due to sensitive information
        if "potentially sensitive information and has been removed" in xml_content:
            logger.warning(f"JUnit XML file {xml_file_path} has been sanitized due to sensitive information")
            return f"JUnit XML file has been sanitized: {xml_content.strip()}"

        # Check if content is empty or not XML
        if not xml_content.strip():
            logger.warning(f"JUnit XML file {xml_file_path} is empty")
            return f"JUnit XML file is empty: {xml_file_path}"

        if not xml_content.strip().startswith("<"):
            logger.warning(f"JUnit XML file {xml_file_path} does not appear to be XML")
            return f"JUnit XML file does not appear to be XML. Content: {xml_content.strip()[:200]}..."

        root = ET.fromstring(xml_content)

        # Find testsuites (handle both root testsuite and nested testsuites)
        testsuites = [root] if root.tag == "testsuite" else root.findall("testsuite")

        failed_testsuites = []
        for testsuite in testsuites:
            failures = int(testsuite.get("failures", "0"))
            errors = int(testsuite.get("errors", "0"))

            if failures > 0 or errors > 0:
                # Remove system-out elements to reduce noise
                for element in testsuite.iter():
                    system_outs = element.findall("system-out")
                    for system_out in system_outs:
                        element.remove(system_out)

                failed_testsuites.append(ET.tostring(testsuite, encoding="unicode"))

        result = "\n".join(failed_testsuites)
        logger.debug(f"Found {len(failed_testsuites)} failed testsuites")
        return result

    except Exception as e:
        error_msg = f"Error getting failed testsuites from {xml_file_path}: {e}"
        logger.error(error_msg)
        return error_msg


@tool(
    name="analyze_screenshot_visual_confirmation",
    description="Analyze a screenshot image along with test failure context using AI",
    show_result=True,
    cache_results=True,
    cache_ttl=300,  # 5 minutes cache
)
def analyze_screenshot_visual_confirmation(
    image_path: str, test_failure_analysis_text: str, test_title: str, junit_xml_failure: str
) -> str:
    """
    Analyze a screenshot image along with provided test failure analysis text.

    Args:
        image_path: The GCS path to the screenshot image
        test_failure_analysis_text: The test failure analysis text
        test_title: The title of the test
        junit_xml_failure: Full test failure/error from the <failure> tag in JUnit XML

    Returns:
        The root cause analysis and screenshot analysis
    """
    try:
        logger.debug(f"Analyzing screenshot: {image_path}")
        logger.debug(f"Test title: {test_title}")

        # Try to get image data
        image_data = None
        try:
            image_bytes = storage_client.get_bytes_from_blob(image_path)
            logger.debug(f"Successfully loaded image data ({len(image_bytes)} bytes)")
            # We'll need to handle the image data in the prompt - for now, note that we have it
            image_data = image_bytes
        except Exception as e:
            logger.warning(f"Could not load image from {image_path}: {e}")
            image_data = None

        # Create prompt based on whether we have image data
        if image_data:
            prompt = f"""
**Objective:** Analyze the provided screenshot from a failed test and the test context to determine the "
            "root cause of the failure. Additionally, describe what the screenshot visually shows and how it "
            "relates to the failure.

**Test Context:**
- Test Name: {test_title}
- Test Failure Analysis: {test_failure_analysis_text}
- JUnit XML Failure: {junit_xml_failure}

**Analysis Requirements:**
1. **Screenshot Description:** Clearly describe the key visual elements in the screenshot. What does the "
            "screenshot show (e.g., UI elements, error messages, application state)?
2. **Screenshot Interpretation:** Explain what the visual information in the screenshot infers or "
            "indicates in relation to the test execution.
3. **Root Cause Analysis:** Based on the screenshot and test context, explain the root cause of the test failure.

Please provide a concise analysis covering these three points. The response must have a claim "
            "specifically detailing what the screenshot shows and infers, and this claim must be supported by "
            "the screenshot.
"""
        else:
            prompt = f"""
**Objective:** Analyze the provided test context to determine the root cause of the failure.

**Test Context:**
- Test Name: {test_title}
- Test Failure Analysis: {test_failure_analysis_text}
- JUnit XML Failure: {junit_xml_failure}

**Analysis Requirements:**
1. **Test Context Analysis:** Analyze the test context to determine the root cause of the failure.
2. **Root Cause Analysis:** Based on the test context, explain the root cause of the test failure.

Please provide a concise analysis covering these two points.
Note: Screenshot analysis was requested but the image could not be loaded from {image_path}.
"""

        # Return the prompt for the agent to process
        # The agent will handle the actual AI model execution
        if image_data:
            return f"""Image analysis requested for {image_path}:

{prompt}

Note: Image data is available ({len(image_data)} bytes) but visual analysis requires AI model execution by the agent."""
        else:
            return prompt

    except Exception as e:
        error_msg = f"Error during screenshot analysis: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool(
    name="get_text_from_file",
    description="Get text content from a file in GCS",
    show_result=True,
    cache_results=True,
    cache_ttl=300,  # 5 minutes cache
)
def get_text_from_file(file_path: str) -> str:
    """
    Get the text from a file from the given file path.

    Args:
        file_path: The path of the file in GCS to get the text of

    Returns:
        The text content of the file
    """
    try:
        logger.debug(f"Getting text from file: {file_path}")
        content = storage_client.get_text_from_blob(file_path)
        logger.debug(f"Retrieved {len(content)} characters from {file_path}")
        return content
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {e}"
        logger.error(error_msg)
        return error_msg


@tool(
    name="get_folder_structure",
    description="Get the tree/folder structure output from a GCS prefix",
    show_result=True,
    cache_results=True,
    cache_ttl=300,  # 5 minutes cache
)
def get_folder_structure(prefix: str) -> str:
    """
    Get the tree/folder structure output from the given prefix.

    Args:
        prefix: The prefix of the folder in GCS to get the structure of

    Returns:
        The tree/folder structure output
    """
    try:
        logger.debug(f"Getting folder structure for: {prefix}")

        blob_names = storage_client.list_blobs(prefix)
        rel_paths = []

        for path in blob_names:
            rel_path = path[len(prefix) :].strip("/")
            if rel_path:
                rel_paths.append(rel_path)

        rel_paths.sort()

        seen_dirs = set()
        tree_output = []

        for path in rel_paths:
            parts = path.split("/")
            for level, part in enumerate(parts):
                current_path = "/".join(parts[: level + 1])
                if current_path not in seen_dirs:
                    seen_dirs.add(current_path)
                    indent = "  " * level  # 2 spaces per level
                    if level == len(parts) - 1:
                        tree_output.append(f"{indent}{part}")
                    else:
                        tree_output.append(f"{indent}{part}/")

        result = "\n".join(tree_output)
        logger.debug(f"Generated tree structure with {len(tree_output)} items")
        return result

    except Exception as e:
        error_msg = f"Error getting folder structure for {prefix}: {e}"
        logger.error(error_msg)
        return error_msg


@tool(
    name="get_immediate_log_files_content",
    description="Get concatenated content of all immediate .log files from a GCS prefix",
    show_result=True,
    cache_results=True,
    cache_ttl=300,  # 5 minutes cache
)
def get_immediate_log_files_content(prefix: str) -> str:
    """
    Get the concatenated content of all immediate .log files from the given prefix.

    Args:
        prefix: The prefix path in GCS to search for immediate .log files

    Returns:
        The concatenated content of all .log files with file names as headers
    """
    try:
        logger.debug(f"Getting immediate log files from: {prefix}")

        # Get all immediate files from the prefix
        immediate_files = storage_client.get_immediate_files(prefix)

        # Filter for .log files
        log_files = [f for f in immediate_files if f.endswith(".log")]

        if not log_files:
            return f"No .log files found in the immediate directory of prefix: {prefix}"

        concatenated_content = []

        for log_file in log_files:
            # Construct full path
            full_path = f"{prefix.rstrip('/')}/{log_file}"

            try:
                # Get content of the log file
                content = storage_client.get_text_from_blob(full_path)

                # Add file header and content
                concatenated_content.append(f"=== {log_file} ===")
                concatenated_content.append(content)
                concatenated_content.append("")  # Empty line for separation

            except Exception as e:
                concatenated_content.append(f"=== {log_file} ===")
                concatenated_content.append(f"Error reading file {log_file}: {e}")
                concatenated_content.append("")

        result = "\n".join(concatenated_content)
        logger.debug(f"Concatenated {len(log_files)} log files")
        return result

    except Exception as e:
        error_msg = f"Error getting immediate log files content from {prefix}: {e}"
        logger.error(error_msg)
        return error_msg


def get_test_analysis_prompt(base_dir: str) -> str:
    """
    Generate the initial test analysis prompt based on the base directory structure.

    Args:
        base_dir: Base directory path in GCS (e.g., "logs/pull/123/test-run-456")

    Returns:
        Generated prompt for test analysis
    """
    try:
        logger.debug(f"Generating test analysis prompt for: {base_dir}")

        job_name = base_dir.split("/")[1]
        logger.debug(f"Job name: {job_name}")

        # Find e2e test directories
        artifacts_dir = f"{base_dir}/artifacts/"
        e2e_dirs = [d for d in storage_client.get_immediate_directories(artifacts_dir) if d.startswith("e2e-tests-")]

        if not e2e_dirs:
            return f"No e2e test directories found in {artifacts_dir}"

        e2e_job_dir = e2e_dirs[0]
        logger.debug(f"E2E job directory: {e2e_job_dir}")

        # Find registry directories
        e2e_job_path = f"{base_dir}/artifacts/{e2e_job_dir}/"
        registry_dirs = [d for d in storage_client.get_immediate_directories(e2e_job_path) if d.endswith("-nightly")]

        if not registry_dirs:
            # No nightly registry found, look for other directories
            all_dirs = storage_client.get_immediate_directories(e2e_job_path)
            logger.debug(f"All directories in {e2e_job_path}: {all_dirs}")

            # Check for build logs in subdirectories
            build_log_prompts = []
            for subdir in all_dirs:
                build_log_path = f"{e2e_job_path}{subdir}/build-log.txt"
                if storage_client.blob_exists(build_log_path):
                    build_log_prompts.append(f"Analyze build log from {build_log_path} using get_text_from_file tool.")

            if build_log_prompts:
                return "CI Job Failed during registry setup (multiple attempts):\n" + "\n".join(build_log_prompts)
            else:
                return f"No test executions or build logs found in {e2e_job_path}"

        registry_dir = registry_dirs[0]
        logger.debug(f"Registry directory: {registry_dir}")

        # Find playwright project result directories
        playwright_artifacts_path = f"{base_dir}/artifacts/{e2e_job_dir}/{registry_dir}/artifacts/"
        playwright_dirs = storage_client.get_immediate_directories(playwright_artifacts_path)

        build_log_path = f"{base_dir}/artifacts/{e2e_job_dir}/{registry_dir}/build-log.txt"

        test_analysis_prompts = []

        for index, playwright_dir in enumerate(playwright_dirs):
            junit_xml_path = f"{playwright_artifacts_path}{playwright_dir}/junit-results.xml"

            if storage_client.blob_exists(junit_xml_path):
                screenshot_base_dir = f"{playwright_artifacts_path}{playwright_dir}/test-results/"
                test_analysis_prompts.append(f"""
{index + 1}. **For Each Failure in JUnit XML ({playwright_dir})**:
    1. **Identify Failure**: Use `get_failed_testsuites` to read and parse `{junit_xml_path}` for failure "
                "messages and screenshot paths. Report screenshot path if found.
    2. **Root Cause Analysis (Mandatory)**:
        a. Construct the full `image_path` by joining `"{screenshot_base_dir}"` with the relative path.
        b. Prepare `test_analysis_text`: a concise summary including the test's purpose and failure message.
        c. **You MUST call for each failure in JUnit XML** "
                "`analyze_screenshot_visual_confirmation(image_path=full_image_path, "
                "test_failure_analysis_text=test_analysis_text, test_title=test_title, "
                "junit_xml_failure=junit_xml_failure)`.
        d. Integrate the response. If error (e.g., image not found), report it.
        e. Return the exact root cause analysis from analyze_screenshot_visual_confirmation.
    3. **Test Purpose**: Describe what the test was trying to verify.
""")
            else:
                pod_logs_dir = f"{playwright_artifacts_path}{playwright_dir}/"
                test_analysis_prompts.append(f"""
{index + 1}. No Test executions found for playwright project: {playwright_dir}.
""")

                if "pod_logs" in storage_client.get_immediate_directories(pod_logs_dir):
                    test_analysis_prompts.append(f"""
Mandatory: Analyze pod logs from "{pod_logs_dir}pod_logs/" for playwright project: "
                f"{playwright_dir} using get_immediate_log_files_content tool(prefix=\"{pod_logs_dir}pod_logs/\").
""")
                else:
                    test_analysis_prompts.append(
                        f"\nAnalyze build log from {build_log_path} using get_text_from_file tool."
                    )

        if not test_analysis_prompts and storage_client.blob_exists(build_log_path):
            test_analysis_prompts.append(
                f"No project-specific artifacts found. Analyze build log from {build_log_path} using "
                "get_text_from_file tool."
            )

        prompt_content = "Analysis Process for EACH Failed Test Case (from JUnit XML) or Project Issue:" + "\n".join(
            test_analysis_prompts
        )

        initial_prompt = f"""
You are an AI expert in test automation analysis. Your goal is to analyze Playwright test failures "
        "based on available artifacts.
You MUST use the provided tools to gather information. Do NOT attempt to access files directly or "
        "assume content is pre-loaded.
Test failure log URL from the prow link: https://prow.ci.openshift.org/view/gs/test-platform-results/{base_dir}

Available Tools:
- `get_failed_testsuites(xml_file_path: str)`: Use this to read specific JUnit XML files.
- `get_text_from_file(file_path: str)`: Use this to read specific, smaller files.
- `analyze_screenshot_visual_confirmation(image_path: str, test_failure_analysis_text: str, "
        "test_title: str, junit_xml_failure: str)`: Use this to analyze a screenshot. Provide the image "
        "path and a summary of the test failure (purpose, failure message, your current analysis). The "
        "tool will return a visual confirmation or insight based on the image.
- `get_immediate_log_files_content(prefix: str)`: Use this to read the content of all immediate .log "
        "files from the given prefix.

{prompt_content}

For each failed test case, structure your response as follows:

    1. Test Case: [Test Case Name]
        a. Test Purpose: [Description]
        b. Failure Message: [From JUnit XML]
        c. Root Cause Analysis: [Root Cause Analysis]
        d. Actionable Recommendations: [Solutions max 2]

For CI/Build failures or pod log issues, structure your response as follows:

    1. Issue Type: [CI Failure/Build Failure/Pod Log Issue]
        a. Issue Description: [Summary of the problem]
        b. Failure Details: [Key error messages and symptoms]
        c. Root Cause Analysis: [Analysis based on logs]
        d. Actionable Recommendations: [Solutions max 2]

Start your analysis.
"""

        logger.debug(f"Generated prompt with {len(test_analysis_prompts)} analysis sections")
        return initial_prompt

    except Exception as e:
        error_msg = f"Error generating test analysis prompt: {e}"
        logger.error(error_msg)
        return error_msg
