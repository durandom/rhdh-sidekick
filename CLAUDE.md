# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sidekick is a modern Python CLI application template built with best practices and production-ready features.

- **uv** for dependency management and virtual environments
- **Typer** for CLI framework with Rich for beautiful output
- **Pydantic** for data validation and settings management
- **Loguru** for structured logging
- **Ruff** for linting and formatting
- **pytest** for testing with coverage

## Development Commands

### Environment Setup
```bash
# Install dependencies (including dev group)
uv sync --group dev
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test types using markers
uv run pytest -m unit          # Unit tests only
uv run pytest -m e2e          # End-to-end tests only
uv run pytest -m "not slow"   # Skip slow tests
```

### Running the Application
```bash
# Run CLI application
uv run sidekick

# Run with debug logging
uv run sidekick -v example hello

# Run with trace logging (most verbose)
uv run sidekick -vv example config

# Try example commands
uv run sidekick example hello --name "Test"
uv run sidekick example config
uv run sidekick version
uv run sidekick info
```

### Code Quality
```bash
# Run linting
uv run ruff check

# Format code
uv run ruff format

# Type checking
uv run mypy src/

# All quality checks
uv run pre-commit run --all-files
```

## Architecture

### CLI Structure
The CLI uses a modular command registry pattern:

- `src/sidekick/cli/base.py` - Base classes and command registry
- `src/sidekick/cli/app.py` - Main CLI application and command registration
- `src/sidekick/commands.py` - Example command implementations
- Commands are organized in modules and registered via `CommandRegistry`

### Configuration Management
- `src/sidekick/settings.py` - Centralized settings using Pydantic
- Supports environment variables with nested delimiter `__` (e.g., `LOGGING__LEVEL=DEBUG`)
- Settings include logging config, API config, and CLI options
- Environment variables automatically override file-based configuration

### Logging Setup
- Configured via `setup_logging()` in `src/sidekick/cli/base.py`
- Supports both "pretty" (colored) and "json" formats
- Can log to console and/or file with rotation
- Logging level and format controlled by settings

**Quick logging examples:**
```bash
# Environment variables
LOG_LEVEL=DEBUG uv run sidekick example hello

# CLI options
uv run sidekick -v example hello              # DEBUG level
uv run sidekick -vv example config            # TRACE level
uv run sidekick --log-level=TRACE example hello
```

**Log locations:**
- **Test logs**: `logs/test-sidekick.log` (automatic during pytest)
- **Application logs**: `logs/sidekick.log` (when configured)
- **Custom logs**: User-specified via CLI or environment variables

### Testing Organization
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for component interactions
- `tests/e2e/` - End-to-end CLI tests using `typer.testing.CliRunner`
- `tests/conftest.py` - Shared pytest fixtures

## Template Usage

This is a CLI application template. To customize for a new project:

1. **Rename the package**: Update `pyproject.toml` and rename `src/sidekick` directory
2. **Update imports**: Change all `sidekick` imports to your new package name
3. **Customize commands**: Modify `commands.py` or create new command modules
4. **Add dependencies**: Use `uv add package-name` for new dependencies
5. **Update documentation**: Modify README.md and this file for your specific use case

### Adding New Commands

1. Create a command group class inheriting from `CommandGroup`
2. Implement the `create_app()` method with your commands
3. Register with `command_registry.register("group-name", YourCommandClass)`
4. Import the module in `cli/app.py` to auto-register

### Example Command Pattern
```python
class MyCommands(CommandGroup):
    def create_app(self) -> typer.Typer:
        app = typer.Typer(help="My command group")

        @app.command()
        def my_command(name: str = "World"):
            """My command description."""
            console.print(f"Hello, {name}!")

        return app

# Register the command group
command_registry.register("my-group", MyCommands)
```

## pdoc Documentation Rules

- **Tool:** Use `pdoc` for API documentation generation from Python source
- **Format:** Strictly use **Google Style Docstrings** for all code elements
- **Public Variables:** Document using PEP 224 docstrings or `#:` doc-comments
- **Output:** Generated documentation located in `docs/sidekick/`
- **Goal:** Maintain consistent, comprehensive, and navigable documentation
- **Audience:** Targeted mainly at developers and LLMs

## Context7 Library IDs

The following Context7-compatible library IDs can be used directly with the `get-library-docs` function:

- **loguru**: `/delgan/loguru` - Python logging made simple
- **pydantic**: `/pydantic/pydantic` - Data validation using Python type hints
- **typer**: `/fastapi/typer` - Build great CLIs based on Python type hints
- **rich**: `/textualize/rich` - Rich text and beautiful formatting in the terminal
- **python-dotenv**: `/theskumar/python-dotenv` - Reads key-value pairs from .env files

## Template Development Guidelines

- Follow SOLID principles for clean architecture
- Use type hints for all public functions
- Write comprehensive tests for new features
- Use Google Style docstrings for documentation
- Maintain high code quality with Ruff and mypy
- Keep the template generic and easily customizable
- Provide clear examples of CLI patterns and best practices
