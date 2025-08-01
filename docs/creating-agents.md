# Creating New Agents

This guide walks through creating a new agent for RHDH Sidekick, from concept to implementation.

## Overview

Agents in RHDH Sidekick are specialized AI assistants that handle specific domains or workflows. They're built on the Agno framework and follow consistent patterns for easy development and maintenance.

## Agent Anatomy

Every agent consists of:

1. **Agent Factory Class** - Inherits from `BaseAgentFactory`
2. **Prompt Template** - YAML file defining agent behavior
3. **CLI Integration** - Command to invoke the agent
4. **Tools** - External integrations the agent can use
5. **Tests** - Unit and integration tests

## Step-by-Step Guide

### Step 1: Plan Your Agent

Before coding, define:
- **Purpose**: What specific problem does this agent solve?
- **Tools Needed**: What external services/APIs will it use?
- **User Interface**: How will users interact with it?
- **Data Requirements**: What information does it need?

### Step 2: Create the Agent Factory

Create a new file in `src/sidekick/agents/your_agent.py`:

```python
"""
Your Agent - Brief description of what it does.
"""

from pathlib import Path
from typing import Any

from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.file import FileTools
from loguru import logger

from .base import BaseAgentFactory
from .mixins import StorageMixin, WorkspaceMixin


class YourAgent(BaseAgentFactory, WorkspaceMixin, StorageMixin):
    """Agent for handling specific tasks."""

    def __init__(
        self,
        storage_path: Path | None = None,
        workspace_dir: Path | None = None,
        memory: Memory | None = None,
        **kwargs
    ):
        """
        Initialize the agent.

        Args:
            storage_path: Path for agent storage
            workspace_dir: Working directory for file operations
            memory: User memory instance
            **kwargs: Additional parameters
        """
        # Initialize base class
        super().__init__(storage_path=storage_path, memory=memory, **kwargs)

        # Initialize mixins
        self._init_workspace_mixin(workspace_dir)
        self._init_storage_mixin()

        # Agent-specific initialization
        self.custom_param = kwargs.get("custom_param", "default")

    def get_display_name(self) -> str:
        """Get display name for the agent."""
        return "your"

    def get_required_env_vars(self) -> list[str]:
        """Return required environment variables."""
        return ["YOUR_API_KEY"]  # Add any required env vars

    async def setup_context(self) -> Any:
        """Setup async context for the agent."""
        # Create any async resources needed
        tools = []

        # Add file tools from workspace mixin
        tools.append(self.create_file_tools())

        # Add your custom tools here
        # tools.append(YourCustomTool())

        return tools

    async def cleanup_context(self, context: Any) -> None:
        """Cleanup async context."""
        # Cleanup any async resources
        pass

    def create_agent(self, tools: list[Any]) -> Agent:
        """Create the configured agent."""
        # Load prompt template
        prompt_template = self.load_prompt_template()

        # Get instructions with any custom variables
        instructions = prompt_template.get_instructions_list(
            custom_var="value"
        )

        # Create storage
        storage = self.create_storage("your_agent")

        # Create and return agent
        return Agent(
            name="Your Agent",
            agent_id="your-agent",
            model=Gemini(),
            tools=tools,
            instructions=instructions,
            storage=storage,
            memory=self.memory,
            show_tool_calls=True,
            markdown=True,
        )
```

### Step 3: Choose and Configure Mixins

Select appropriate mixins based on your agent's needs:

#### Available Mixins

**StorageMixin** - For persistent storage
```python
class YourAgent(BaseAgentFactory, StorageMixin):
    def __init__(self, ...):
        self._init_storage_mixin()

    def create_agent(self, ...):
        storage = self.create_storage("table_name")
```

**WorkspaceMixin** - For file operations
```python
class YourAgent(BaseAgentFactory, WorkspaceMixin):
    def __init__(self, workspace_dir: Path | None = None, ...):
        self._init_workspace_mixin(workspace_dir)

    def setup_context(self):
        tools = [self.create_file_tools()]
```

**JiraMixin** - For Jira integration
```python
class YourAgent(BaseAgentFactory, JiraMixin):
    def __init__(self, ...):
        self._init_jira_mixin(read_only=False)

    async def setup_context(self):
        return await self.create_jira_context()
```

**KnowledgeMixin** - For RAG capabilities
```python
class YourAgent(BaseAgentFactory, KnowledgeMixin):
    def __init__(self, knowledge_path: Path | None = None, ...):
        self._init_knowledge_mixin(knowledge_path)

    async def setup_context(self):
        await self.load_knowledge_base()
        tools = [self.create_knowledge_tools()]
```

### Step 4: Create the Prompt Template

Create `src/sidekick/prompts/templates/agents/your.yaml`:

```yaml
name: your_agent
version: "1.0"
description: "Agent for handling specific tasks"

# Variables that can be customized
variables:
  workspace_dir: "/tmp/your_agent"
  custom_setting: "default_value"

# Include common instructions
includes:
  - shared/common_instructions.yaml

# Main template
template: |
  You are an AI assistant specialized in [your domain].

  WORKSPACE:
  You have access to a workspace directory at: {{workspace_dir}}
  Use this for any file operations or temporary storage.

  CAPABILITIES:
  - Capability 1: Description
  - Capability 2: Description
  - Capability 3: Description

  GUIDELINES:
  1. Always validate input before processing
  2. Provide clear, actionable responses
  3. Use tools effectively to accomplish tasks

  WORKFLOW:
  When asked to perform a task:
  1. Understand the requirements
  2. Plan the approach
  3. Execute using available tools
  4. Verify the results
  5. Provide a clear summary

  {{custom_setting}}

  Remember to:
  - Be helpful and thorough
  - Explain your actions
  - Handle errors gracefully
```

### Step 5: Add CLI Integration

Add to `src/sidekick/cli/chat.py` or create a new command file:

```python
@chat_app.command("your")
def chat_your(
    ctx: typer.Context,
    initial_query: str | None = typer.Argument(
        None,
        help="Initial query to start the conversation"
    ),
    workspace: Path = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Workspace directory for file operations"
    ),
    custom_param: str = typer.Option(
        "default",
        "--custom",
        help="Custom parameter for your agent"
    ),
) -> None:
    """Start an interactive chat with Your Agent."""
    try:
        # Check environment variables
        if not os.getenv("YOUR_API_KEY"):
            console.print("[red]Error: YOUR_API_KEY not set[/red]")
            raise typer.Exit(1)

        # Create agent factory
        from ..agents.your_agent import YourAgent

        agent_factory = YourAgent(
            storage_path=get_default_storage_path("your"),
            workspace_dir=workspace,
            memory=create_memory(_user_id),
            custom_param=custom_param,
        )

        # Run interactive chat
        asyncio.run(
            run_interactive_chat(
                agent_factory=agent_factory,
                initial_query=initial_query,
                streaming=_streaming_enabled,
            )
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Chat ended by user[/yellow]")
    except Exception as e:
        logger.exception("Error in Your Agent chat")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
```

### Step 6: Add Custom Tools (Optional)

If your agent needs custom tools beyond the standard ones:

```python
# src/sidekick/tools/your_tool.py
from typing import Any
from pydantic import BaseModel, Field

class YourToolInput(BaseModel):
    """Input for your tool."""
    param1: str = Field(..., description="Parameter 1")
    param2: int = Field(default=10, description="Parameter 2")

class YourTool:
    """Custom tool for your agent."""

    def __init__(self, config: Any):
        self.config = config

    def process(self, input_data: YourToolInput) -> str:
        """Process the input and return results."""
        # Tool implementation
        return f"Processed {input_data.param1} with {input_data.param2}"

    def get_tools(self) -> list:
        """Return tool definition for Agno."""
        return [self.process]
```

### Step 7: Write Tests

Create `tests/unit/test_your_agent.py`:

```python
"""Tests for YourAgent."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from sidekick.agents.your_agent import YourAgent


class TestYourAgent:
    """Test suite for YourAgent."""

    def test_init(self, tmp_path):
        """Test agent initialization."""
        agent = YourAgent(
            storage_path=tmp_path / "storage.db",
            workspace_dir=tmp_path / "workspace",
        )

        assert agent.storage_path == tmp_path / "storage.db"
        assert agent.workspace_dir == tmp_path / "workspace"

    def test_required_env_vars(self):
        """Test required environment variables."""
        agent = YourAgent()
        env_vars = agent.get_required_env_vars()

        assert "YOUR_API_KEY" in env_vars

    @pytest.mark.asyncio
    async def test_setup_context(self, tmp_path):
        """Test context setup."""
        agent = YourAgent(workspace_dir=tmp_path)

        tools = await agent.setup_context()

        assert len(tools) > 0
        # Add specific tool assertions

    def test_create_agent(self, tmp_path):
        """Test agent creation."""
        agent_factory = YourAgent(
            storage_path=tmp_path / "storage.db",
            workspace_dir=tmp_path / "workspace",
        )

        with patch.object(agent_factory, 'load_prompt_template'):
            tools = []
            agent = agent_factory.create_agent(tools)

            assert agent.name == "Your Agent"
            assert agent.agent_id == "your-agent"
```

## Best Practices

### 1. Use Mixins for Common Functionality

Don't duplicate code. If multiple agents need similar functionality, use or create a mixin:

```python
# Good
class MyAgent(BaseAgentFactory, JiraMixin, WorkspaceMixin):
    pass

# Bad - duplicating Jira setup code
class MyAgent(BaseAgentFactory):
    def setup_jira(self):
        # 50 lines of duplicated code
```

### 2. Keep Prompts Focused

Each agent should have a clear, specific purpose:

```yaml
# Good - specific and focused
template: |
  You are a code review assistant specialized in Python projects.
  Focus on: code quality, best practices, and security issues.

# Bad - too broad
template: |
  You are a general programming assistant that can do everything.
```

### 3. Handle Errors Gracefully

Always validate inputs and handle errors:

```python
def create_agent(self, tools):
    # Validate required configuration
    if not self.api_key:
        raise ValueError("API key is required")

    try:
        # Agent creation
        return Agent(...)
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise
```

### 4. Document Tool Usage

In your prompt template, clearly document available tools:

```yaml
template: |
  AVAILABLE TOOLS:
  - search_knowledge: Search the knowledge base for information
    Example: search_knowledge("authentication methods")

  - create_file: Create a new file in the workspace
    Example: create_file("config.yaml", "content here")
```

### 5. Test Thoroughly

Write tests for:
- Initialization with various parameters
- Tool creation and configuration
- Error handling
- Integration with mixins

## Common Patterns

### Pattern 1: Read-Only vs Read-Write Agents

```python
class ReadOnlyAgent(BaseAgentFactory, JiraMixin):
    def __init__(self, ...):
        self._init_jira_mixin(read_only=True)  # Read-only access

class ReadWriteAgent(BaseAgentFactory, JiraMixin):
    def __init__(self, ...):
        self._init_jira_mixin(read_only=False)  # Full access
```

### Pattern 2: Multi-Tool Agents

```python
async def setup_context(self):
    tools = []

    # Add multiple tool sets
    tools.append(self.create_file_tools())
    tools.extend(await self.create_jira_tools())
    tools.append(self.create_knowledge_tools())

    return tools
```

### Pattern 3: Configurable Behavior

```python
def create_agent(self, tools):
    # Load different templates based on mode
    template_name = f"agents.your.{self.mode}"
    prompt_template = self.load_prompt_template(template_name)
```

## Troubleshooting

### Common Issues

1. **Agent not loading**
   - Check imports in `__init__.py`
   - Verify CLI registration
   - Check for syntax errors

2. **Tools not working**
   - Verify tool initialization in `setup_context`
   - Check tool permissions and API keys
   - Review tool call formatting in prompts

3. **Poor agent responses**
   - Review and refine prompt template
   - Ensure tools are properly documented
   - Check instruction clarity

### Debugging Tips

1. Enable debug logging:
   ```bash
   uv run sidekick -v chat your
   ```

2. Test tools independently:
   ```python
   # In a test or script
   tool = YourTool()
   result = tool.process(input_data)
   print(result)
   ```

3. Validate prompt rendering:
   ```bash
   uv run sidekick prompts show agents.your --format
   ```

## Next Steps

After creating your agent:

1. **Documentation** - Update README.md with usage examples
2. **Examples** - Add example scripts in `examples/`
3. **Integration** - Consider team agents if coordination is needed
4. **Optimization** - Profile and optimize for common use cases
5. **Feedback** - Get user feedback and iterate

Remember: Good agents are focused, well-documented, and easy to use. Start simple and enhance based on real user needs.
