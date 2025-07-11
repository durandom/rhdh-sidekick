# GitHub Copilot Instructions for B4rt

## Project Overview

B4rt is a stream analysis tool for racing telemetry built with Python, using modern tooling and best practices.

**Key Technologies:**
- **uv** for dependency management and virtual environments
- **Typer** for CLI framework with Rich for beautiful output
- **Pydantic** for data validation and settings management
- **Loguru** for structured logging
- **Ruff** for linting and formatting
- **pytest** for testing with coverage

## Development Workflow

### Running the Application
```bash
# Run CLI application
uv run b4rt
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test types using markers
uv run pytest -m unit          # Unit tests only
uv run pytest -m "not slow"   # Skip slow tests
```

### Code Quality and Pre-commit

**Always run before committing:**
```bash
make prepare-commit  # Main commit preparation using pre-commit hooks
```

**Individual quality checks:**
```bash
make lint        # Run ruff linting with fixes
make format      # Run ruff code formatting
make typecheck   # Run mypy type checking
make test        # Run pytest test suite
make quality     # Run all quality checks (lint + typecheck + test)
```

## Coding Standards

### SOLID Principles
Follow SOLID principles:
- **Single Responsibility**: A class or function should have one purpose only
- **Open/Closed**: Classes should be open for extension but closed for modification
- **Liskov Substitution**: Subclasses should be substitutable for their base classes
- **Interface Segregation**: Split large interfaces into smaller, specific ones
- **Dependency Inversion**: High-level code should depend on abstractions, not concrete implementations

### Code Quality Requirements
- **Type Hints**: Always use type hints for function parameters and return types
- **Constants**: Avoid "magic numbers" or "magic strings" - use constants for fixed values
- **Data Structures**: Use data classes or enums for structured data
- **Documentation**: Use Google Style Docstrings for all public functions, classes, and methods

### Testing Organization
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for component interactions
- `tests/e2e/` - End-to-end CLI tests using `typer.testing.CliRunner`
- `tests/conftest.py` - Shared pytest fixtures
- `tests/fixtures/` - Test data files

## Commit Guidelines

### Conventional Commit Format
Use the format: `<emoji> <type>: <description>`

**Common types with emojis:**
- ✨ `feat`: A new feature
- 🐛 `fix`: A bug fix
- 📝 `docs`: Documentation changes
- 💄 `style`: Code style changes (formatting, etc)
- ♻️ `refactor`: Code changes that neither fix bugs nor add features
- ⚡️ `perf`: Performance improvements
- ✅ `test`: Adding or fixing tests
- 🔧 `chore`: Changes to the build process, tools, etc.
- 🚨 `fix`: Fix compiler/linter warnings
- 🔒️ `fix`: Fix security issues

### Commit Best Practices
- **Present tense, imperative mood**: Write as commands (e.g., "add feature" not "added feature")
- **Atomic commits**: Each commit should contain related changes serving a single purpose
- **Concise first line**: Keep under 72 characters
- **Verify before committing**: Always run `make prepare-commit` first

## Repository Structure

```
src/
├── b4rt/           # Main application code
│   ├── cli/        # CLI interface and commands
│   ├── core/       # Core business logic
│   └── utils/      # Utility functions
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/            # End-to-end tests
├── conftest.py     # Shared fixtures
└── fixtures/       # Test data
```

## Development Guidelines

### Before Starting Work
1. Run `make validate-tooling` to check if tools would make changes
2. Run `make quality` to ensure starting from clean state

### During Development
- Use `make lint` for quick linting with auto-fixes
- Use `make format` for code formatting
- Use `make typecheck` for type checking

### Before Committing
1. **Always run `make prepare-commit`** - this is mandatory
2. Ensure all tests pass with `make test`
3. Use conventional commit format with appropriate emoji
4. Consider splitting large changes into multiple logical commits

### Error Handling
- Use structured logging with Loguru
- Implement proper exception handling
- Provide meaningful error messages to users

## Important Notes

- **Fail fast**: The pre-commit process stops on first tool failure
- **Consistent tooling**: All tools use aligned configurations to avoid conflicts
- **CLI-first**: This is a CLI application - design with command-line usage in mind
- **Type safety**: Leverage Pydantic for data validation and type safety
- **Testing**: Write tests for all new functionality - prefer unit tests over integration tests where possible

## Dependencies Management

- Use `uv` for all dependency management
- Add new dependencies to `pyproject.toml`
- Pin critical dependencies to specific versions when needed
- Run `uv sync --group dev` after adding dependencies

## pdoc Documentation Rules

- **Tool:** Use `pdoc` for API documentation generation from Python source.
- **Format:** Strictly use **Google Style Docstrings** for all code elements (functions, methods, classes).
- **Public Variables:** Document public variables using either PEP 224 docstrings or `#:` doc-comments. `pdoc` parses the source code to find these.
  - **PEP 224:** Place a string literal immediately after the variable assignment.
    ```python
    module_variable = 1
    """PEP 224 docstring for module_variable."""
    ```
  - **`#:` Comment:** Place a comment starting with `#:` immediately before the variable assignment. Can span multiple lines.
    ```python
    class C:
        #: Documentation comment for class_variable
        #: spanning over multiple lines.
        class_variable = 2
    ```
  - **Instance Variables:** Document in `__init__` using either method. PEP 224 takes precedence if both are present.
    ```python
    def __init__(self):
        #: Instance variable doc-comment
        self.instance_var = 3
        """PEP 224 docstring takes precedence."""
    ```
- **Output:** Generated documentation is located in `docs/b4rt/`. Keep this directory updated via `pdoc`.
- **Goal:** Maintain consistent, comprehensive, and navigable documentation.
- **Audience:** Targeted maninly at large language models (LLMs), i.e. the documentation should be easy to parse and understand, dense in informa


## Further Reading

Visit the CLAUDE.md file for more detailed guidelines on architecture, testing organization, and documentation rules if needed
