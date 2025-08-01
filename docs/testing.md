# Testing Guide

This guide covers testing strategies, patterns, and best practices for RHDH Sidekick.

## Overview

RHDH Sidekick uses pytest for all testing, with a focus on:
- **Unit tests** for individual components
- **Integration tests** for component interactions
- **End-to-end tests** for CLI commands
- **Mock-based testing** for external dependencies

## Test Structure

```
tests/
├── conftest.py          # Shared fixtures and configuration
├── unit/                # Unit tests
│   ├── test_agents.py
│   ├── test_cli.py
│   └── test_utils.py
├── integration/         # Integration tests
│   ├── test_agent_integration.py
│   └── test_knowledge_integration.py
└── e2e/                # End-to-end CLI tests
    ├── test_chat_commands.py
    └── test_knowledge_commands.py
```

## Running Tests

### Basic Commands

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_agents.py

# Run specific test
uv run pytest tests/unit/test_agents.py::TestJiraAgent::test_init

# Run tests matching pattern
uv run pytest -k "jira"
```

### With Coverage

```bash
# Generate coverage report
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Test Markers

```bash
# Run only unit tests
uv run pytest -m unit

# Run only e2e tests
uv run pytest -m e2e

# Skip slow tests
uv run pytest -m "not slow"
```

## Writing Tests

### Test File Naming

- Unit tests: `test_<module>.py`
- Integration tests: `test_<feature>_integration.py`
- E2E tests: `test_<command>_commands.py`

### Basic Test Structure

```python
"""Tests for YourModule."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from sidekick.your_module import YourClass


class TestYourClass:
    """Test suite for YourClass."""

    def test_initialization(self):
        """Test class initialization."""
        instance = YourClass(param="value")
        assert instance.param == "value"

    def test_method_success(self):
        """Test method with successful outcome."""
        instance = YourClass()
        result = instance.method("input")
        assert result == "expected"

    def test_method_error(self):
        """Test method error handling."""
        instance = YourClass()
        with pytest.raises(ValueError):
            instance.method(None)

    @pytest.mark.asyncio
    async def test_async_method(self):
        """Test async method."""
        instance = YourClass()
        result = await instance.async_method()
        assert result is not None
```

## Testing Patterns

### 1. Testing Agents

```python
class TestMyAgent:
    """Test suite for MyAgent."""

    @pytest.fixture
    def agent_factory(self, tmp_path):
        """Create agent factory for testing."""
        return MyAgent(
            storage_path=tmp_path / "storage.db",
            workspace_dir=tmp_path / "workspace"
        )

    def test_required_env_vars(self, agent_factory):
        """Test environment variable requirements."""
        env_vars = agent_factory.get_required_env_vars()
        assert "MY_API_KEY" in env_vars

    @pytest.mark.asyncio
    async def test_setup_context(self, agent_factory):
        """Test context setup."""
        with patch('sidekick.tools.MyTool') as mock_tool:
            context = await agent_factory.setup_context()
            assert mock_tool.called
            assert len(context) > 0

    def test_create_agent(self, agent_factory):
        """Test agent creation."""
        with patch.object(agent_factory, 'load_prompt_template') as mock_prompt:
            mock_prompt.return_value.get_instructions_list.return_value = ["instruction"]

            tools = []
            agent = agent_factory.create_agent(tools)

            assert agent.name == "My Agent"
            assert agent.agent_id == "my-agent"
```

### 2. Testing CLI Commands

```python
from typer.testing import CliRunner
from sidekick.cli.app import app

runner = CliRunner()

class TestCLICommands:
    """Test suite for CLI commands."""

    def test_version_command(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "sidekick version" in result.stdout

    def test_chat_command_no_env(self):
        """Test chat command without required env vars."""
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(app, ["chat", "jira"])
            assert result.exit_code == 1
            assert "JIRA_SERVER_URL not set" in result.stdout

    @patch('sidekick.cli.chat.asyncio.run')
    def test_chat_command_success(self, mock_run):
        """Test successful chat command."""
        with patch.dict(os.environ, {"JIRA_SERVER_URL": "https://test"}):
            result = runner.invoke(app, ["chat", "jira", "test query"])
            assert result.exit_code == 0
            mock_run.assert_called_once()
```

### 3. Testing with Fixtures

```python
@pytest.fixture
def mock_jira_client():
    """Mock Jira client for testing."""
    client = Mock()
    client.search_issues.return_value = [
        {"key": "TEST-1", "summary": "Test Issue"}
    ]
    return client

@pytest.fixture
def knowledge_manager(tmp_path):
    """Create knowledge manager for testing."""
    from sidekick.knowledge import KnowledgeManager

    return KnowledgeManager(
        knowledge_path=tmp_path / "knowledge",
        index_path=tmp_path / "index"
    )

class TestWithFixtures:
    """Test using fixtures."""

    def test_with_mock_jira(self, mock_jira_client):
        """Test with mocked Jira client."""
        issues = mock_jira_client.search_issues("query")
        assert len(issues) == 1
        assert issues[0]["key"] == "TEST-1"

    async def test_with_knowledge_manager(self, knowledge_manager, tmp_path):
        """Test with knowledge manager."""
        # Create test document
        doc_path = tmp_path / "knowledge" / "test.md"
        doc_path.parent.mkdir(parents=True)
        doc_path.write_text("Test content")

        # Test loading
        await knowledge_manager.load_documents()
        assert knowledge_manager.document_count > 0
```

### 4. Testing Async Code

```python
@pytest.mark.asyncio
class TestAsyncCode:
    """Test async functionality."""

    async def test_async_method(self):
        """Test basic async method."""
        instance = AsyncClass()
        result = await instance.async_method()
        assert result == "expected"

    async def test_async_with_mock(self):
        """Test async with mocked dependencies."""
        mock_service = AsyncMock()
        mock_service.fetch_data.return_value = {"data": "value"}

        instance = AsyncClass(service=mock_service)
        result = await instance.process()

        mock_service.fetch_data.assert_called_once()
        assert result["data"] == "value"

    async def test_async_context_manager(self):
        """Test async context manager."""
        async with AsyncContextManager() as manager:
            result = await manager.operation()
            assert result is not None
```

### 5. Testing External APIs

```python
class TestExternalAPIs:
    """Test external API interactions."""

    @patch('requests.get')
    def test_api_call_success(self, mock_get):
        """Test successful API call."""
        mock_get.return_value.json.return_value = {"status": "ok"}
        mock_get.return_value.status_code = 200

        client = APIClient()
        result = client.get_status()

        assert result["status"] == "ok"
        mock_get.assert_called_with("https://api.example.com/status")

    @patch('requests.get')
    def test_api_call_error(self, mock_get):
        """Test API error handling."""
        mock_get.side_effect = requests.RequestException("Network error")

        client = APIClient()
        with pytest.raises(APIError):
            client.get_status()
```

## Test Fixtures

### Common Fixtures in conftest.py

```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_workspace():
    """Create temporary workspace directory."""
    workspace = Path(tempfile.mkdtemp())
    yield workspace
    shutil.rmtree(workspace)

@pytest.fixture
def mock_env():
    """Mock environment variables."""
    env = {
        "JIRA_SERVER_URL": "https://test.jira.com",
        "JIRA_TOKEN": "test-token",
        "GITHUB_ACCESS_TOKEN": "test-github-token",
    }
    with patch.dict(os.environ, env):
        yield env

@pytest.fixture
def sample_knowledge_docs(tmp_path):
    """Create sample knowledge documents."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "doc1.md").write_text("# Document 1\nContent here")
    (docs_dir / "doc2.md").write_text("# Document 2\nMore content")

    return docs_dir

@pytest.fixture
async def async_client():
    """Create async client for testing."""
    client = AsyncClient()
    await client.connect()
    yield client
    await client.disconnect()
```

## Mocking Strategies

### 1. Mocking File Operations

```python
def test_file_operations(tmp_path):
    """Test file operations with tmp_path."""
    file_path = tmp_path / "test.txt"

    # Write file
    file_path.write_text("content")

    # Test function that reads file
    result = read_file(file_path)
    assert result == "content"
```

### 2. Mocking External Services

```python
@patch('sidekick.utils.jira_client.JIRA')
def test_jira_integration(mock_jira_class):
    """Test Jira integration with mocked client."""
    # Setup mock
    mock_instance = Mock()
    mock_jira_class.return_value = mock_instance
    mock_instance.issue.return_value = {"key": "TEST-1"}

    # Test
    client = JiraClient()
    issue = client.get_issue("TEST-1")

    assert issue["key"] == "TEST-1"
    mock_instance.issue.assert_called_with("TEST-1")
```

### 3. Mocking Async Dependencies

```python
async def test_async_dependency():
    """Test with mocked async dependency."""
    mock_service = AsyncMock()
    mock_service.fetch.return_value = {"result": "data"}

    processor = DataProcessor(service=mock_service)
    result = await processor.process()

    mock_service.fetch.assert_awaited_once()
    assert result["result"] == "data"
```

## Testing Best Practices

### 1. Test Isolation

Each test should be independent:

```python
# Good - isolated test
def test_isolated(tmp_path):
    """Each test gets its own tmp_path."""
    config = Config(path=tmp_path / "config.json")
    config.save({"key": "value"})
    assert config.load()["key"] == "value"

# Bad - tests depend on shared state
class TestWithSharedState:
    shared_data = []

    def test_first(self):
        self.shared_data.append("item")  # Modifies shared state

    def test_second(self):
        assert len(self.shared_data) == 1  # Depends on test_first
```

### 2. Descriptive Test Names

```python
# Good - descriptive names
def test_agent_initialization_with_custom_storage_path():
    """Test that agent initializes correctly with custom storage path."""
    pass

def test_jira_search_returns_empty_list_when_no_results():
    """Test that Jira search returns empty list when no results found."""
    pass

# Bad - unclear names
def test_1():
    pass

def test_agent():
    pass
```

### 3. Arrange-Act-Assert Pattern

```python
def test_with_aaa_pattern():
    """Test following Arrange-Act-Assert pattern."""
    # Arrange
    agent = MyAgent()
    input_data = {"query": "test"}

    # Act
    result = agent.process(input_data)

    # Assert
    assert result is not None
    assert result["status"] == "success"
```

### 4. Testing Error Cases

Always test both success and failure paths:

```python
class TestErrorHandling:
    """Test error handling."""

    def test_success_case(self):
        """Test successful operation."""
        result = divide(10, 2)
        assert result == 5

    def test_division_by_zero(self):
        """Test division by zero handling."""
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)

    def test_invalid_input(self):
        """Test invalid input handling."""
        with pytest.raises(TypeError):
            divide("10", 2)
```

### 5. Use Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input, expected):
    """Test uppercase conversion with multiple inputs."""
    assert input.upper() == expected

@pytest.mark.parametrize("agent_type,expected_tools", [
    ("jira", ["search_issues", "create_issue"]),
    ("github", ["search_repos", "create_pr"]),
    ("search", ["search_knowledge", "index_documents"]),
])
def test_agent_tools(agent_type, expected_tools):
    """Test different agents have correct tools."""
    agent = create_agent(agent_type)
    tools = agent.get_tool_names()
    for tool in expected_tools:
        assert tool in tools
```

## Performance Testing

### Basic Performance Tests

```python
import time
import pytest

def test_performance():
    """Test operation completes within time limit."""
    start = time.time()

    # Operation to test
    result = expensive_operation()

    duration = time.time() - start
    assert duration < 1.0  # Should complete in under 1 second
    assert result is not None

@pytest.mark.slow
def test_large_dataset_performance():
    """Test performance with large dataset."""
    data = generate_large_dataset(10000)

    start = time.time()
    result = process_data(data)
    duration = time.time() - start

    assert duration < 5.0  # Should handle 10k items in under 5 seconds
    assert len(result) == 10000
```

## Debugging Tests

### Using pytest Debugging Features

```bash
# Drop into debugger on failure
uv run pytest --pdb

# Show local variables on failure
uv run pytest -l

# Show full traceback
uv run pytest --tb=long

# Capture print statements
uv run pytest -s

# Run last failed tests
uv run pytest --lf

# Run failed tests first, then others
uv run pytest --ff
```

### Adding Debug Output

```python
def test_with_debug_output(capfd):
    """Test with captured output for debugging."""
    print("Debug: Starting test")

    result = complex_operation()
    print(f"Debug: Result = {result}")

    # Capture output
    out, err = capfd.readouterr()

    # Can assert on output if needed
    assert "Starting test" in out
    assert result == "expected"
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install uv
      run: pip install uv

    - name: Install dependencies
      run: uv sync --group dev

    - name: Run tests
      run: uv run pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Test Maintenance

### Regular Tasks

1. **Remove obsolete tests** when features are removed
2. **Update tests** when APIs change
3. **Add tests** for bug fixes
4. **Refactor tests** to reduce duplication
5. **Review coverage** reports for gaps

### Test Organization Tips

1. Group related tests in classes
2. Use descriptive module and class names
3. Keep test files focused and manageable
4. Extract common setup to fixtures
5. Document complex test scenarios

Remember: Good tests are as important as good code. They provide confidence in changes and serve as documentation for how the system should behave.
