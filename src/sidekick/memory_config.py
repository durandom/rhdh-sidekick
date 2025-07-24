"""
Memory configuration utilities for agents and teams.

This module provides consistent memory configuration for all agents and teams
using SqliteMemoryDb with a shared database file but different table names.
"""

import os
from pathlib import Path

from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini


def get_memory_db_path() -> Path:
    """Get the shared database path for memory storage.

    Returns:
        Path to the memory database file
    """
    return Path("tmp/sidekick.db")


def create_memory_instance(table_name: str, model_id: str = "gemini-2.5-flash") -> Memory:
    """Create a Memory instance with consistent configuration.

    Args:
        table_name: Unique table name for this agent/team's memories
        model_id: Model ID to use for memory operations

    Returns:
        Configured Memory instance
    """
    db_file = get_memory_db_path()

    # Ensure the directory exists
    db_file.parent.mkdir(parents=True, exist_ok=True)

    memory_db = SqliteMemoryDb(table_name=table_name, db_file=str(db_file))

    return Memory(model=Gemini(id=model_id), db=memory_db)


def get_user_id() -> str:
    """Get the user ID for memory operations.

    Returns the user ID from the global app state or environment variable,
    falling back to a default value if none is set.

    Returns:
        User ID string
    """
    try:
        from .cli.app import _user_id

        if _user_id:
            return _user_id
    except ImportError:
        pass

    # Fallback to environment variable or default
    return os.getenv("USER", "default_user")
