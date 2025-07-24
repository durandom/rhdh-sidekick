"""
State management toolkit for team session coordination.

Provides async tools for generic state manipulation using the ToolKit pattern.
"""

from datetime import datetime
from typing import Any

from agno.tools import Toolkit


class StateManagementToolkit(Toolkit):
    """Async toolkit for generic state management operations."""

    def __init__(self, state: dict[str, Any]):
        """Initialize with a reference to the state dictionary."""
        super().__init__(name="state_management")
        self.state = state

    async def set_state_value(self, key: str, value: str) -> str:
        """Set a value in the session state.

        Args:
            key: The state key to set
            value: The value to set

        Returns:
            Success message
        """
        self.state[key] = value
        return f"Set {key}: {value}"

    async def track_item(self, collection_key: str, item_key: str, summary: str, **extra_fields) -> str:
        """Track an item in a collection with optional extra fields.

        Args:
            collection_key: The collection to track in (e.g., 'analyzed_tickets')
            item_key: Unique identifier for the item
            summary: Brief summary of the item
            **extra_fields: Additional fields to store with the item

        Returns:
            Success message
        """
        item = {"key": item_key, "summary": summary, "timestamp": datetime.now().isoformat(), **extra_fields}

        # Get existing collection or create new one
        items = self.state.get(collection_key, [])

        # Try to update existing item first
        for existing_item in items:
            if isinstance(existing_item, dict) and existing_item.get("key") == item_key:
                existing_item.update(item)
                return f"Updated {collection_key} tracking for {item_key}"

        # Add new item
        items.append(item)
        self.state[collection_key] = items
        return f"Added item to {collection_key} tracking: {item_key}"

    async def link_items(
        self, links_key: str, from_key: str, to_key: str, relationship: str = "related", **extra_fields
    ) -> str:
        """Create a relationship link between two items.

        Args:
            links_key: The links collection to store in (e.g., 'ticket_pr_links')
            from_key: The source item key
            to_key: The target item key
            relationship: Type of relationship (e.g., 'implements', 'fixes', 'relates_to')
            **extra_fields: Additional fields to store with the link

        Returns:
            Success message
        """
        link_data = {"to_key": to_key, "relationship": relationship, **extra_fields}

        # Get existing links or create new structure
        links = self.state.get(links_key, {})
        if from_key not in links:
            links[from_key] = []

        # Check if link already exists
        for existing_link in links[from_key]:
            if isinstance(existing_link, dict) and existing_link.get("to_key") == to_key:
                existing_link.update(link_data)
                self.state[links_key] = links
                return f"Updated link: {from_key} {relationship} {to_key}"

        # Add new link
        links[from_key].append(link_data)
        self.state[links_key] = links
        return f"Created link: {from_key} {relationship} {to_key}"

    async def get_state_summary(self, keys: str = "") -> str:
        """Get a formatted summary of the current session state.

        Args:
            keys: Comma-separated list of state keys to summarize (empty for all)

        Returns:
            Formatted summary of the state
        """
        if keys:
            key_list = [k.strip() for k in keys.split(",")]
        else:
            # Default keys to summarize (skip internal keys)
            key_list = []
            for key in self.state:
                if not key.startswith("_") and key not in ["session_start_time"]:
                    key_list.append(key)

        return self._get_summary(key_list)

    def _get_summary(self, keys: list[str], max_items_per_key: int = 5) -> str:
        """Generate a formatted summary of specified keys."""
        summary_parts = []

        for key in keys:
            value = self.state.get(key)
            if not value:
                continue

            if isinstance(value, list):
                count = len(value)
                items_to_show = value[-max_items_per_key:] if count > max_items_per_key else value
                summary_parts.append(f"**{key.replace('_', ' ').title()} ({count}):**")

                for item in items_to_show:
                    if isinstance(item, dict):
                        # Try to find a reasonable display format
                        display = item.get("key") or item.get("id") or item.get("name") or str(item)
                        summary = item.get("summary", "")
                        if summary:
                            summary_parts.append(f"- {display}: {summary}")
                        else:
                            summary_parts.append(f"- {display}")
                    else:
                        summary_parts.append(f"- {item}")

            elif isinstance(value, dict):
                count = sum(len(v) if isinstance(v, list) else 1 for v in value.values())
                summary_parts.append(f"**{key.replace('_', ' ').title()} ({count}):**")

                for nested_key, nested_value in list(value.items())[:max_items_per_key]:
                    if isinstance(nested_value, list):
                        for item in nested_value:
                            if isinstance(item, dict):
                                relationship = item.get("relationship", "related")
                                target = item.get("to_key") or item.get("pr_key") or item.get("key") or str(item)
                                summary_parts.append(f"- {nested_key} {relationship} {target}")
                            else:
                                summary_parts.append(f"- {nested_key}: {item}")
                    else:
                        summary_parts.append(f"- {nested_key}: {nested_value}")

            else:
                summary_parts.append(f"**{key.replace('_', ' ').title()}:** {value}")

        return "\n".join(summary_parts) if summary_parts else "No data available"


class AgentStateManagementToolkit(Toolkit):
    """Async toolkit for agent-specific state management with attribution."""

    def __init__(self, state: dict[str, Any], agent_name: str):
        """Initialize with state reference and agent name for attribution."""
        super().__init__(name=f"agent_state_management_{agent_name.lower().replace(' ', '_')}")
        self.state = state
        self.agent_name = agent_name

    async def record_analysis(self, collection_key: str, item_key: str, summary: str) -> str:
        """Record an analysis performed by this agent.

        Args:
            collection_key: Collection to record in (e.g., 'analyzed_tickets')
            item_key: Unique identifier for the analyzed item
            summary: Summary of the analysis

        Returns:
            Success message
        """
        item = {
            "key": item_key,
            "summary": summary,
            "analyzed_by": self.agent_name,
            "timestamp": datetime.now().isoformat(),
        }

        # Get existing collection
        items = self.state.get(collection_key, [])

        # Try to update existing item
        for existing_item in items:
            if isinstance(existing_item, dict) and existing_item.get("key") == item_key:
                existing_item.update(item)
                return f"Updated analysis record for {item_key}"

        # Add new item
        items.append(item)
        self.state[collection_key] = items
        return f"Recorded analysis of {item_key} by {self.agent_name}"

    async def create_link(
        self, links_key: str, from_key: str, to_key: str, relationship: str = "related", **extra_fields
    ) -> str:
        """Create a link between items, noting the discovering agent.

        Args:
            links_key: Links collection key
            from_key: Source item key
            to_key: Target item key
            relationship: Type of relationship
            **extra_fields: Additional fields

        Returns:
            Success message
        """
        extra_fields["discovered_by"] = self.agent_name

        links = self.state.get(links_key, {})
        if from_key not in links:
            links[from_key] = []

        link_data = {"to_key": to_key, "relationship": relationship, **extra_fields}

        # Check if link already exists
        for existing_link in links[from_key]:
            if isinstance(existing_link, dict) and existing_link.get("to_key") == to_key:
                existing_link.update(link_data)
                self.state[links_key] = links
                return f"Updated link: {from_key} {relationship} {to_key}"

        # Add new link
        links[from_key].append(link_data)
        self.state[links_key] = links
        return f"Created link: {from_key} {relationship} {to_key} (discovered by {self.agent_name})"

    async def get_analyzed_summary(self) -> str:
        """Get what has been analyzed so far in this session.

        Returns:
            Summary of analyzed items
        """
        summary_parts = []

        # Look for common analysis collections
        for key in self.state:
            if "analyzed" in key.lower() or "tracked" in key.lower():
                items = self.state.get(key, [])
                if items:
                    item_keys = []
                    for item in items:
                        if isinstance(item, dict):
                            item_keys.append(item.get("key", str(item)))
                        else:
                            item_keys.append(str(item))
                    summary_parts.append(f"{key.replace('_', ' ').title()}: {', '.join(item_keys)}")

        # Look for links
        for key in self.state:
            if "link" in key.lower():
                links = self.state.get(key, {})
                if links:
                    link_count = sum(len(v) if isinstance(v, list) else 1 for v in links.values())
                    summary_parts.append(f"{key.replace('_', ' ').title()}: {link_count} connections")

        return "; ".join(summary_parts) if summary_parts else "No items analyzed yet in this session"
