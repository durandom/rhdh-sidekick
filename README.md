# sidekick - Modern Python CLI Application

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A modern Python CLI application with AI-powered search capabilities built with Typer, Rich, and Pydantic.

## 🚀 Setup

```bash
# Install dependencies
uv sync --group dev

# Verify installation
uv run sidekick --help
```

## 🔍 Search Command

The main feature of sidekick is its AI-powered search functionality that uses RAG (Retrieval-Augmented Generation) to search through knowledge bases.

### Basic Usage

```bash
# Search for information
uv run sidekick search "your search query here"

# Example searches
uv run sidekick search "How to install RHDH on OpenShift?"
uv run sidekick search "What are the authentication methods?"
uv run sidekick search "Explain the plugin architecture"
```

### Interactive Mode

The search command runs in interactive mode by default. After each search result, you can:

- Enter a new query to continue searching
- Press Enter to exit the search session

### Verbose Logging

```bash
# Enable debug logging
uv run sidekick -v search "your query"

# Enable trace logging
uv run sidekick -vv search "your query"
```

## Other Commands

```bash
# Show version
uv run sidekick version

# Show application info
uv run sidekick info
```

## License

Creative Commons Attribution-NonCommercial 4.0 - Free for personal/educational use, no commercial use.
