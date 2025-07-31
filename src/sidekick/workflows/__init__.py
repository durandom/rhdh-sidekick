"""
Workflows module for orchestrating multi-agent processes.

This module contains workflow implementations that coordinate multiple
agents to accomplish complex tasks.
"""

from .release_notes import ReleaseNotesGenerator
from .research_workflow import ResearchWorkflow, run_research_workflow

__all__ = ["ReleaseNotesGenerator", "ResearchWorkflow", "run_research_workflow"]
