# Modern Python Project Blueprint 2.0

A comprehensive guide for bootstrapping world-class Python projects based on the battle-tested patterns from the B4 Racing Team platform. This blueprint emphasizes a tool-driven approach using modern Python tooling to ensure consistency, quality, and developer efficiency.

## Table of Contents

- [Project Initialization](#project-initialization)
- [Core Tooling & Architecture](#core-tooling--architecture)
- [Project Structure](#project-structure)
- [Quality & Verification](#quality--verification)
- [Documentation Standards](#documentation-standards)
- [Advanced Patterns](#advanced-patterns)
- [CLI Development](#cli-development)
- [Configuration Management](#configuration-management)
- [Testing Strategy](#testing-strategy)
- [Production Deployment](#production-deployment)

## Project Initialization

### 1. Setup with `uv`

Modern Python dependency management with `uv` for blazing-fast installs and reproducible environments:

```bash
# Initialize in existing directory
mkdir my-python-project && cd my-python-project
uv init --package

# Test the project works
uv run my-python-project
```

**What `uv init --package` creates:**
- `.gitignore` - Comprehensive Python gitignore
- `.python-version` - Python version specification
- `README.md` - Project documentation
- `pyproject.toml` - Project configuration and dependencies
- `src/my_python_project/` - Source code directory
- `src/my_python_project/__init__.py` - Package initialization with main() function

**Note:** `uv` automatically manages virtual environments - no manual `uv venv` or activation needed!

### 2. Enhanced pyproject.toml Configuration

After `uv init --package --name my-python-project`, enhance the generated `pyproject.toml` with production-ready configuration:

```toml
[project]
name = "my-python-project"
version = "0.1.0"
description = "Modern Python project with best practices"
readme = "README.md"
requires-python = ">=3.12"
authors = [
    {name = "Your Name", email = "your.email@domain.com"}
]
dependencies = [
    "loguru>=0.7.3",           # Modern logging
    "pydantic>=2.11.5",        # Data validation and settings
    "typer>=0.9.0",            # CLI framework
    "rich>=13.0.0",            # Rich terminal output
    "python-dotenv>=1.0.0",    # Environment variable management
]

# CLI entry point - uv creates this automatically
[project.scripts]
my-python-project = "my_python_project:main"

# Build system - uv adds this automatically
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# Code quality with Ruff
[tool.ruff]
line-length = 120
src = ["src", "tests"]
target-version = "py312"

[tool.ruff.lint]
# Enable comprehensive linting rules
select = ["E", "F", "W", "I", "B", "UP", "PT", "SIM"]
ignore = []
fixable = ["E501", "I"]

[tool.ruff.format]
indent-style = "space"
line-ending = "auto"
quote-style = "double"
skip-magic-trailing-comma = false

# Testing configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow running tests",
]

# Coverage configuration
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]

# Development dependencies
[dependency-groups]
dev = [
    "ruff>=0.11.12",           # Linting and formatting
    "pytest>=8.4.0",          # Testing framework
    "pytest-asyncio>=1.0.0",  # Async testing support
    "pytest-cov>=6.1.1",      # Coverage reporting
    "pre-commit>=3.0.0",      # Git hooks
]
docs = [
    "pdoc>=14.0.0",           # API documentation
    "mkdocs>=1.5.0",          # Documentation site
    "mkdocs-material>=9.0.0", # Material theme
]
```

### 3. Development Workflow Commands

```bash
# Add dependencies after uv init
uv add loguru pydantic typer rich python-dotenv

# Add development dependencies
uv add --group dev ruff pytest pytest-asyncio pytest-cov pre-commit

# Install all dependencies (including dev group)
uv sync --group dev

# Update all dependencies
uv lock --upgrade

# Run your CLI application
uv run my-python-project

# Run with arguments
uv run my-python-project --help
```

### 4. Enhanced Entry Point

`uv init --package` creates a basic `src/my_python_project/__init__.py`. Enhance it for production use:

```python
# src/my_python_project/__init__.py
"""
My Python Project

A modern Python application built with best practices.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console

# Import settings and configure logging
from .settings import settings
from .cli.base import setup_logging

__version__ = "0.1.0"

# Configure console for rich output
console = Console()

def main() -> None:
    """Main entry point for the CLI application."""
    # Setup logging based on settings
    setup_logging(settings.logging)

    # Import the main CLI app
    from .cli.app import app

    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

This enhanced entry point provides:
- ✅ **Error handling** with graceful user feedback
- ✅ **Logging setup** based on configuration
- ✅ **Rich console output** for better UX
- ✅ **Modular CLI** imported from separate modules

## Core Tooling & Architecture

### 1. Code Quality with Ruff

Ultra-fast Python linter and formatter that replaces flake8, black, and isort:

```bash
# Check code quality
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Check in CI
uv run ruff check . --output-format=github
```

**Configuration benefits:**
- ✅ 10-100x faster than traditional tools
- ✅ Single tool replaces multiple linters
- ✅ Native Python AST parsing
- ✅ Extensive rule set with auto-fixes

### 2. Data Models with Pydantic

Modern data validation and settings management:

```python
# models.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class User(BaseModel):
    """User model with validation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    name: str = Field(min_length=1, max_length=200)
    email: str = Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')
    age: Optional[int] = Field(None, ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.now)

# Usage
user = User(name="Alice", email="alice@example.com", age=30)
print(user.model_dump())  # Serialization
print(user.model_dump_json())  # JSON serialization
```

**Settings Management:**

```python
# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "sqlite:///app.db"
    database_pool_size: int = 10

    # API
    api_host: str = "localhost"
    api_port: int = 8000
    api_key: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

# Global settings instance
settings = Settings()
```

### 3. CLI with Typer and Rich

Production-ready CLI with beautiful output:

```python
# cli.py
import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path

app = typer.Typer(help="My awesome CLI application")
console = Console()

@app.command()
def list_files(
    directory: Path = typer.Argument(Path("."), help="Directory to list"),
    show_hidden: bool = typer.Option(False, "--hidden", "-h", help="Show hidden files"),
    format_table: bool = typer.Option(True, "--table", help="Format as table"),
) -> None:
    """List files in a directory with beautiful output."""

    if not directory.exists():
        console.print(f"[red]Error: Directory {directory} does not exist[/red]")
        raise typer.Exit(1)

    files = [f for f in directory.iterdir() if show_hidden or not f.name.startswith('.')]

    if format_table:
        table = Table(title=f"Files in {directory}")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Size", style="green")

        for file in files:
            file_type = "📁 Directory" if file.is_dir() else "📄 File"
            size = str(file.stat().st_size) if file.is_file() else "-"
            table.add_row(file.name, file_type, size)

        console.print(table)
    else:
        for file in files:
            console.print(f"{'📁' if file.is_dir() else '📄'} {file.name}")

if __name__ == "__main__":
    app()
```

**Advanced CLI Patterns:**

```python
# cli_commands/__init__.py
from .data import app as data_app
from .models import app as models_app

# main.py
import typer
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path.cwd() / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Main app with subcommands
app = typer.Typer(help="Production CLI with subcommands")

# Register command groups
app.add_typer(data_app, name="data", help="Data management commands")
app.add_typer(models_app, name="models", help="Model operations")

if __name__ == "__main__":
    app()
```

## Project Structure

### Standard Directory Layout

**After `uv init --package my-python-project`:**

```
my-python-project/
├── .gitignore                 # Auto-generated by uv
├── .python-version           # Python version specification
├── README.md                 # Auto-generated project docs
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file (created on first uv add)
└── src/
    └── my_python_project/
        └── __init__.py      # Contains main() function
```

**Enhanced structure for production projects:**

```
my-python-project/
├── .github/
│   └── workflows/
│       ├── test.yml           # CI/CD pipeline
│       └── publish.yml        # Package publishing
├── .gitignore                 # Enhanced by adding project-specific patterns
├── .python-version           # Auto-generated by uv
├── .pre-commit-config.yaml    # Git hooks configuration
├── README.md                  # Enhanced project documentation
├── pyproject.toml            # Enhanced configuration
├── uv.lock                   # Dependency lock file
├── src/
│   └── my_python_project/
│       ├── __init__.py       # Main entry point (enhanced)
│       ├── cli/              # CLI commands (add manually)
│       │   ├── __init__.py
│       │   ├── base.py       # Command base classes
│       │   └── data.py       # Data commands
│       ├── models.py         # Pydantic models
│       ├── settings.py       # Configuration management
│       ├── core/             # Core business logic
│       │   ├── __init__.py
│       │   └── service.py
│       └── utils/            # Utility functions
│           ├── __init__.py
│           └── helpers.py
├── tests/                    # Add manually
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── unit/                # Unit tests
│   │   ├── __init__.py
│   │   └── test_models.py
│   ├── integration/         # Integration tests
│   │   ├── __init__.py
│   │   └── test_service.py
│   └── fixtures/            # Test data
│       └── sample_data.json
├── docs/                    # Add manually
│   ├── api/                 # API documentation
│   ├── guides/             # User guides
│   └── development.md       # Development guide
└── scripts/                 # Add manually
    ├── setup.sh
    └── deploy.sh
```

### Enhanced .gitignore with Curated Templates

**Note:** `uv init --package` creates a basic `.gitignore`, but enhance it with GitHub's curated templates:

```bash
# Fetch comprehensive Python gitignore from GitHub
curl -L https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore > .gitignore

# Add platform-specific patterns
curl -L https://raw.githubusercontent.com/github/gitignore/main/Global/VisualStudioCode.gitignore >> .gitignore
curl -L https://raw.githubusercontent.com/github/gitignore/main/Global/macOS.gitignore >> .gitignore
curl -L https://raw.githubusercontent.com/github/gitignore/main/Global/Windows.gitignore >> .gitignore
```

**Add project-specific patterns:**

```bash
# Add project-specific patterns to the gitignore
cat >> .gitignore << 'EOF'

# Project-specific directories
/data/
/output/
/cache/
/logs/

# Environment files
.env.local
.env.*.local

# Documentation builds
/docs/_build/
/site/

# Temporary files
*.tmp
*.temp
*.log
EOF
```

**Complete workflow:**

```bash
# 1. Initialize project with uv (includes basic .gitignore)
uv init my-project --package
cd my-project

# 2. Replace with comprehensive GitHub templates
curl -L https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore > .gitignore
curl -L https://raw.githubusercontent.com/github/gitignore/main/Global/VisualStudioCode.gitignore >> .gitignore
curl -L https://raw.githubusercontent.com/github/gitignore/main/Global/macOS.gitignore >> .gitignore

# 3. Add project-specific patterns
echo -e "\n# Project specific\n/data/\n/output/\n*.log" >> .gitignore

# 4. Initialize git and commit
git init
git add .
git commit -m "Initial project setup with comprehensive gitignore"
```

**Benefits:**
- ✅ **Community-maintained** and regularly updated
- ✅ **Comprehensive coverage** of Python, IDE, and OS patterns
- ✅ **Always current** with latest best practices

## Quality & Verification

### 1. Testing with pytest

Modern testing framework with async support:

```python
# tests/conftest.py
import pytest
import asyncio
from pathlib import Path

@pytest.fixture
def sample_data():
    """Provide sample data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30
    }

@pytest.fixture
def temp_directory(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# tests/unit/test_models.py
import pytest
from pydantic import ValidationError
from my_python_project.models import User

class TestUser:
    """Test cases for User model."""

    def test_valid_user_creation(self, sample_data):
        """Test creating a valid user."""
        user = User(**sample_data)
        assert user.name == sample_data["name"]
        assert user.email == sample_data["email"]
        assert user.age == sample_data["age"]

    def test_invalid_email_raises_error(self):
        """Test that invalid email raises validation error."""
        with pytest.raises(ValidationError):
            User(name="Test", email="invalid-email", age=30)

    @pytest.mark.parametrize("age", [-1, 151, "invalid"])
    def test_invalid_age_raises_error(self, age):
        """Test that invalid age raises validation error."""
        with pytest.raises(ValidationError):
            User(name="Test", email="test@example.com", age=age)

# tests/integration/test_service.py
import pytest
from my_python_project.core.service import UserService

@pytest.mark.asyncio
class TestUserService:
    """Integration tests for UserService."""

    async def test_create_user(self, sample_data):
        """Test creating a user through the service."""
        service = UserService()
        user = await service.create_user(sample_data)
        assert user.name == sample_data["name"]

    @pytest.mark.slow
    async def test_bulk_user_creation(self):
        """Test creating multiple users (slow test)."""
        service = UserService()
        users_data = [{"name": f"User {i}", "email": f"user{i}@example.com"}
                     for i in range(100)]
        users = await service.create_users_bulk(users_data)
        assert len(users) == 100
```

### 2. Pre-commit Hooks

Automatic code quality checks before commits:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]

# Setup
uv add --group dev pre-commit
uv run pre-commit install
```

### 3. GitHub Actions CI/CD

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Install dependencies
      run: |
        uv sync --group dev

    - name: Lint with ruff
      run: |
        uv run ruff check .
        uv run ruff format --check .

    - name: Type check with mypy
      run: |
        uv run mypy src/

    - name: Test with pytest
      run: |
        uv run pytest --cov=src --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Documentation Standards

### 1. Google Style Docstrings

```python
"""Module for user management functionality.

This module provides classes and functions for managing user data,
including validation, storage, and retrieval operations.

Example:
    Basic usage of the User class:

    >>> user = User(name="Alice", email="alice@example.com")
    >>> print(user.name)
    'Alice'
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class UserManager:
    """Manages user operations with validation and storage.

    This class provides a high-level interface for user management,
    including creation, updates, and queries with proper validation.

    Attributes:
        storage_backend: The storage backend instance for persistence.
        validation_enabled: Whether to perform strict validation.

    Example:
        >>> manager = UserManager()
        >>> user = manager.create_user("Alice", "alice@example.com")
        >>> print(user.name)
        'Alice'
    """

    def __init__(self, storage_backend: Optional[str] = None) -> None:
        """Initialize the UserManager.

        Args:
            storage_backend: Optional storage backend type. Defaults to 'memory'.
        """
        self.storage_backend = storage_backend or "memory"
        self.validation_enabled = True

    def create_user(
        self,
        name: str,
        email: str,
        age: Optional[int] = None
    ) -> User:
        """Create a new user with validation.

        Creates a new user instance with the provided data. Performs
        validation on all fields and raises appropriate errors for
        invalid data.

        Args:
            name: The user's full name (1-200 characters).
            email: Valid email address with proper format.
            age: Optional age (0-150). Defaults to None.

        Returns:
            User: The created and validated user instance.

        Raises:
            ValidationError: If any field validation fails.
            ValueError: If user with email already exists.

        Example:
            >>> manager = UserManager()
            >>> user = manager.create_user("Bob", "bob@example.com", 25)
            >>> print(f"Created user: {user.name}")
            'Created user: Bob'
        """
        # Implementation here
        pass

    def find_users_by_age_range(
        self,
        min_age: int,
        max_age: int
    ) -> List[User]:
        """Find users within a specific age range.

        Searches for all users whose age falls within the specified
        range (inclusive). Returns an empty list if no users match.

        Args:
            min_age: Minimum age (inclusive).
            max_age: Maximum age (inclusive).

        Returns:
            List[User]: List of users matching the age criteria.

        Raises:
            ValueError: If min_age > max_age or negative ages provided.

        Example:
            >>> users = manager.find_users_by_age_range(18, 30)
            >>> print(f"Found {len(users)} users")
            'Found 5 users'
        """
        # Implementation here
        pass
```

### 2. API Documentation with pdoc

```bash
# Generate API documentation
uv run pdoc --html --output-dir docs/api src/my_python_project

# Serve documentation locally
uv run pdoc --http localhost:8080 src/my_python_project
```

### 3. Type Hints Everywhere

```python
from typing import Union, Optional, List, Dict, Any, Callable, TypeVar, Generic
from pathlib import Path
from datetime import datetime

T = TypeVar('T')

class Repository(Generic[T]):
    """Generic repository pattern with type safety."""

    def __init__(self, model_class: type[T]) -> None:
        self.model_class = model_class

    def find_by_id(self, id: int) -> Optional[T]:
        """Find entity by ID with type safety."""
        # Implementation
        pass

    def find_all(self) -> List[T]:
        """Find all entities with proper return typing."""
        # Implementation
        pass

def process_file(
    file_path: Union[str, Path],
    processors: List[Callable[[str], str]],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[str, int, datetime]]:
    """Process file with multiple processors and return metadata.

    Args:
        file_path: Path to the file to process.
        processors: List of processing functions to apply.
        options: Optional processing configuration.

    Returns:
        Dictionary containing processing results and metadata.
    """
    # Implementation with full type safety
    pass
```

## Advanced Patterns

### 1. Factory Pattern with Type Safety

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Dict, Any
from pydantic import BaseModel

ConfigT = TypeVar('ConfigT', bound=BaseModel)

class Component(Generic[ConfigT], ABC):
    """Abstract base component with typed configuration."""

    CONFIG_CLASS: Type[ConfigT]
    DEFAULT_CONFIG: ConfigT

    def __init__(self, config: ConfigT) -> None:
        self.config = config

    @classmethod
    def create_default(cls) -> 'Component[ConfigT]':
        """Create component with default configuration."""
        return cls(cls.DEFAULT_CONFIG)

    @classmethod
    def create_with_config(cls, config: ConfigT) -> 'Component[ConfigT]':
        """Create component with custom configuration."""
        return cls(config)

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process data according to component logic."""
        pass

# Concrete implementation
class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"

class DatabaseComponent(Component[DatabaseConfig]):
    """Database component with typed configuration."""

    CONFIG_CLASS = DatabaseConfig
    DEFAULT_CONFIG = DatabaseConfig()

    def process(self, query: str) -> List[Dict[str, Any]]:
        """Execute database query."""
        # Implementation
        pass

# Usage with perfect type safety
db = DatabaseComponent.create_default()
custom_db = DatabaseComponent.create_with_config(
    DatabaseConfig(host="production.db", port=5433)
)
```

### 2. Registry Pattern for Extensibility

```python
from typing import Dict, Type, TypeVar, Optional
import inspect

T = TypeVar('T')

class Registry(Generic[T]):
    """Type-safe registry for component registration."""

    def __init__(self) -> None:
        self._registry: Dict[str, Type[T]] = {}

    def register(self, name: str, component_class: Type[T]) -> None:
        """Register a component class."""
        self._registry[name] = component_class

    def get(self, name: str) -> Optional[Type[T]]:
        """Get registered component class."""
        return self._registry.get(name)

    def list_available(self) -> List[str]:
        """List all registered component names."""
        return list(self._registry.keys())

    def create_instance(self, name: str, *args, **kwargs) -> Optional[T]:
        """Create instance of registered component."""
        component_class = self.get(name)
        if component_class:
            return component_class(*args, **kwargs)
        return None

# Usage
processor_registry = Registry[Component]()
processor_registry.register("database", DatabaseComponent)
processor_registry.register("cache", CacheComponent)

# Create instances dynamically
db_processor = processor_registry.create_instance("database")
```

### 3. Event System with Type Safety

```python
from typing import Protocol, List, Callable, TypeVar, Any
from dataclasses import dataclass
from datetime import datetime

class Event(Protocol):
    """Event protocol for type checking."""
    timestamp: datetime
    event_type: str

@dataclass
class UserCreatedEvent:
    """Type-safe event for user creation."""
    timestamp: datetime
    event_type: str = "user_created"
    user_id: int
    user_email: str

EventT = TypeVar('EventT', bound=Event)
EventHandler = Callable[[EventT], None]

class EventBus:
    """Type-safe event bus for decoupled communication."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler[EventT]) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: EventT) -> None:
        """Publish an event to all subscribers."""
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log error but continue processing
                print(f"Error handling event {event.event_type}: {e}")

# Usage
event_bus = EventBus()

def handle_user_created(event: UserCreatedEvent) -> None:
    print(f"User {event.user_email} created at {event.timestamp}")

event_bus.subscribe("user_created", handle_user_created)
event_bus.publish(UserCreatedEvent(
    timestamp=datetime.now(),
    user_id=123,
    user_email="alice@example.com"
))
```

## CLI Development

### 1. Dynamic CLI with Registry Pattern

```python
# cli_commands/base.py
from abc import ABC, abstractmethod
from typing import Dict, Type
import typer

class CommandGroup(ABC):
    """Abstract base for CLI command groups."""

    @abstractmethod
    def create_app(self) -> typer.Typer:
        """Create the Typer app for this command group."""
        pass

class CommandRegistry:
    """Registry for CLI command groups."""

    def __init__(self) -> None:
        self._commands: Dict[str, Type[CommandGroup]] = {}

    def register(self, name: str, command_class: Type[CommandGroup]) -> None:
        """Register a command group."""
        self._commands[name] = command_class

    def create_main_app(self) -> typer.Typer:
        """Create main app with all registered commands."""
        app = typer.Typer(help="My CLI Application")

        for name, command_class in self._commands.items():
            command_instance = command_class()
            command_app = command_instance.create_app()
            app.add_typer(command_app, name=name)

        return app

# cli_commands/data.py
class DataCommands(CommandGroup):
    """Data management commands."""

    def create_app(self) -> typer.Typer:
        app = typer.Typer(help="Data management operations")

        @app.command()
        def list(
            format: str = typer.Option("table", help="Output format"),
            limit: int = typer.Option(10, help="Number of items to show"),
        ) -> None:
            """List data items."""
            # Implementation
            pass

        @app.command()
        def process(
            input_file: Path,
            output_dir: Path = typer.Option(Path("output"), help="Output directory"),
        ) -> None:
            """Process data files."""
            # Implementation
            pass

        return app

# main.py
registry = CommandRegistry()
registry.register("data", DataCommands)
registry.register("models", ModelCommands)

app = registry.create_main_app()

if __name__ == "__main__":
    app()
```

### 2. Rich Progress and Tables

```python
from rich.progress import Progress, TaskID
from rich.table import Table
from rich.console import Console
from typing import List, Dict, Any
import time

def process_with_progress(items: List[Any]) -> None:
    """Process items with a beautiful progress bar."""

    with Progress() as progress:
        task = progress.add_task("[cyan]Processing items...", total=len(items))

        for item in items:
            # Simulate processing
            time.sleep(0.1)
            process_item(item)
            progress.advance(task)

def display_results_table(results: List[Dict[str, Any]]) -> None:
    """Display results in a formatted table."""

    console = Console()
    table = Table(title="Processing Results")

    # Add columns
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Duration", style="yellow")

    # Add rows
    for result in results:
        status_style = "green" if result["success"] else "red"
        table.add_row(
            str(result["id"]),
            result["name"],
            f"[{status_style}]{result['status']}[/{status_style}]",
            f"{result['duration']:.2f}s"
        )

    console.print(table)
```

## Configuration Management

### 1. Hierarchical Configuration

```python
# config.py
from typing import Optional, Dict, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import yaml
import json

class DatabaseConfig(BaseModel):
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    username: str = "user"
    password: str = "password"
    pool_size: int = 10

class APIConfig(BaseModel):
    """API configuration."""
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    reload: bool = False

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"
    file: Optional[Path] = None

class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # App settings
    app_name: str = "My Python Project"
    debug: bool = False
    environment: str = "development"

    # Component configs
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'Settings':
        """Load settings from YAML or JSON file."""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
            with open(config_path) as f:
                data = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            with open(config_path) as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")

        return cls(**data)

    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """Save current settings to file."""
        config_path = Path(config_path)

        data = self.model_dump()

        if config_path.suffix.lower() in ['.yaml', '.yml']:
            with open(config_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)

# Usage
settings = Settings()  # Load from environment
# or
settings = Settings.from_file("config.yaml")  # Load from file

# Environment variables override file settings:
# DATABASE__HOST=prod.db DATABASE__PORT=5433 python app.py
```

### 2. Environment-based Configuration

```yaml
# config/development.yaml
database:
  host: localhost
  port: 5432
  database: myapp_dev

api:
  port: 8000
  reload: true

logging:
  level: DEBUG
  format: pretty
```

```yaml
# config/production.yaml
database:
  host: prod-db.example.com
  port: 5432
  database: myapp_prod
  pool_size: 20

api:
  port: 80
  workers: 4

logging:
  level: INFO
  format: json
  file: /var/log/myapp.log
```

## Testing Strategy

### 1. Test Organization

```python
# tests/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_database() -> AsyncGenerator[Database, None]:
    """Provide test database instance."""
    db = Database(":memory:")
    await db.initialize()
    yield db
    await db.cleanup()

@pytest.fixture
def sample_user_data():
    """Provide sample user data."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30
    }

# tests/unit/test_models.py
class TestUserModel:
    """Unit tests for User model."""

    def test_valid_user_creation(self, sample_user_data):
        user = User(**sample_user_data)
        assert user.name == sample_user_data["name"]

    @pytest.mark.parametrize("invalid_email", [
        "invalid",
        "@example.com",
        "test@",
        "",
    ])
    def test_invalid_email_validation(self, invalid_email):
        with pytest.raises(ValidationError):
            User(name="Test", email=invalid_email)

# tests/integration/test_service.py
@pytest.mark.asyncio
class TestUserService:
    """Integration tests for UserService."""

    async def test_create_and_retrieve_user(self, test_database, sample_user_data):
        service = UserService(test_database)

        # Create user
        user = await service.create_user(sample_user_data)
        assert user.id is not None

        # Retrieve user
        retrieved = await service.get_user(user.id)
        assert retrieved.name == sample_user_data["name"]

# tests/e2e/test_cli.py
from typer.testing import CliRunner

class TestCLI:
    """End-to-end CLI tests."""

    def test_list_command(self):
        runner = CliRunner()
        result = runner.invoke(app, ["data", "list"])

        assert result.exit_code == 0
        assert "No data found" in result.stdout

    def test_process_command_with_file(self, tmp_path):
        # Create test file
        test_file = tmp_path / "test.json"
        test_file.write_text('{"test": "data"}')

        runner = CliRunner()
        result = runner.invoke(app, ["data", "process", str(test_file)])

        assert result.exit_code == 0
```

### 2. Coverage and Quality Gates

```bash
# Run tests with coverage
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Coverage configuration in pyproject.toml ensures:
# - Minimum 80% coverage
# - Exclude test files from coverage
# - Generate both HTML and terminal reports

# Quality gates in CI:
# - All tests must pass
# - Coverage >= 80%
# - No linting errors
# - Type checking passes
```

## Production Deployment

### 1. Docker Container

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set Python path
ENV PYTHONPATH=/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uv", "run", "python", "-m", "my_python_project.main"]
```

### 2. Production Settings

```python
# production_settings.py
from .settings import Settings

class ProductionSettings(Settings):
    """Production-specific settings."""

    # Override defaults for production
    debug: bool = False
    environment: str = "production"

    # Production database with connection pooling
    database: DatabaseConfig = DatabaseConfig(
        host="prod-db.example.com",
        port=5432,
        pool_size=20,
        connection_timeout=30,
    )

    # Production API with multiple workers
    api: APIConfig = APIConfig(
        host="0.0.0.0",
        port=8000,
        workers=4,
        reload=False,
    )

    # Structured logging for production
    logging: LoggingConfig = LoggingConfig(
        level="INFO",
        format="json",
        file="/var/log/myapp.log",
    )
```

### 3. Monitoring and Observability

```python
# monitoring.py
import time
import functools
from typing import Callable, Any
from loguru import logger

def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            logger.info(
                f"Function {func.__name__} completed",
                duration=duration,
                success=True
            )

            return result

        except Exception as e:
            duration = time.time() - start_time

            logger.error(
                f"Function {func.__name__} failed",
                duration=duration,
                error=str(e),
                success=False
            )

            raise

    return wrapper

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
    }
```

## Development Workflow

### 1. Daily Development Commands

```bash
# Development setup
uv sync --group dev
uv run pre-commit install

# Code quality checks
uv run ruff check . --fix
uv run ruff format .
uv run mypy src/

# Testing
uv run pytest
uv run pytest --cov=src --cov-report=html
uv run pytest -m "not slow"  # Skip slow tests

# Documentation
uv run pdoc --html src/
uv run mkdocs serve  # If using mkdocs
```

### 2. Git Workflow

```bash
# Feature development
git checkout -b feature/new-feature
# Make changes...
git add .
# Pre-commit hooks run automatically
git commit -m "feat: add new feature"
git push origin feature/new-feature
# Create pull request
```

### 3. Release Process

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
git tag v1.0.0
git push origin v1.0.0
# GitHub Actions will build and publish automatically
```

## Conclusion

This blueprint provides a solid foundation for modern Python projects with:

✅ **Modern Tooling**: uv, ruff, typer, pydantic, rich
✅ **Type Safety**: Full type hints with mypy validation
✅ **Quality Assurance**: Pre-commit hooks, comprehensive testing, CI/CD
✅ **Production Ready**: Docker, monitoring, structured logging
✅ **Developer Experience**: Rich CLI, beautiful output, excellent documentation
✅ **Extensibility**: Registry patterns, factory methods, modular architecture

The patterns demonstrated here scale from simple scripts to complex production systems while maintaining code quality and developer productivity.
