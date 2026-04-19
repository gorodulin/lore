import os

from lore.facts.create_fact import create_fact
from lore.facts.edit_fact import edit_fact
from lore.facts.delete_fact import delete_fact
from lore.facts.match_facts_for_path import match_facts_for_path
from lore.facts.read_fact import read_fact
from lore.client.try_send_fact_request import try_send_fact_request


class ToolSet:
    """Binds project_root into tool methods for MCP registration."""

    def __init__(self, project_root: str):
        self._root = project_root

    def handle_create_fact(self, fact: str, incl: list[str], skip: list[str] | None = None, tags: list[str] | None = None) -> dict:
        """Record a convention or lesson to be surfaced when matching files
        are touched. Keep text short and actionable - a reminder, not docs.
        Always discuss with the user before creating.

        Patterns: "p:<glob>" for paths, "c:<regex>" for content. Combine
        to narrow scope. Use skip for exceptions. Auto-placed in the
        nearest .lore.json by directory prefix of incl patterns.

        Args:
            fact: Short, actionable reminder text.
            incl: Inclusion patterns (e.g. ["p:src/**/*.py", "c:import logging"]).
            skip: Optional exclusion patterns (same format as incl).
            tags: Optional tags (e.g. ["hook:read", "kind:convention"]).
        """
        return create_fact(self._root, fact, incl, skip, tags=tags)

    def handle_find_facts(self, file_path: str) -> dict:
        """Find conventions and constraints that apply to a file. Call when
        working on a file to see what guardrails exist for it.

        Args:
            file_path: Path relative to project root (e.g. "src/api/auth.py").
        """
        content = None
        full_path = os.path.join(self._root, file_path)
        if os.path.isfile(full_path):
            try:
                with open(full_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                pass
        params = {"file_path": file_path}
        if content is not None:
            params["content"] = content
        server_result = try_send_fact_request(self._root, "find_facts", params)
        if server_result is not None:
            return server_result
        return match_facts_for_path(self._root, file_path, content=content)

    def handle_read_fact(self, fact_id: str) -> dict:
        """Read a single fact by its ID.

        Returns full definition (text, patterns, location). Use before
        editing or deleting to inspect current state.

        Args:
            fact_id: The ID of the fact to read.
        """
        return read_fact(self._root, fact_id)

    def handle_edit_fact(self, fact_id: str, fact: str | None = None, incl: list[str] | None = None, skip: list[str] | None = None, tags: list[str] | None = None) -> dict:
        """Edit an existing fact. Only provided fields are changed;
        omitted fields keep existing values. Use `read_fact` first.

        Patterns: "p:<glob>" for paths, "c:<regex>" for content.

        Args:
            fact_id: The ID of the fact to edit.
            fact: New fact text (omit to keep existing).
            incl: New inclusion patterns (omit to keep existing).
            skip: New exclusion patterns (omit to keep existing).
            tags: New tags (omit to keep existing).
        """
        return edit_fact(self._root, fact_id, fact_text=fact, incl=incl, skip=skip, tags=tags)

    def handle_delete_fact(self, fact_id: str) -> dict:
        """Delete a fact by its ID. Empty .lore.json files are
        auto-deleted.

        Args:
            fact_id: The ID of the fact to delete.
        """
        return delete_fact(self._root, fact_id)


def register_mcp_tools(mcp, project_root: str) -> None:
    """Register all lore tools on a FastMCP instance.

    Each tool is a bound method on a ToolSet instance, so project_root
    is captured without nested function definitions.

    Args:
        mcp: A FastMCP instance to register tools on.
        project_root: Absolute path to the project root directory.
    """
    tools = ToolSet(project_root)
    mcp.tool(tools.handle_create_fact, name="create_fact")
    mcp.tool(tools.handle_find_facts, name="find_facts")
    mcp.tool(tools.handle_read_fact, name="read_fact")
    mcp.tool(tools.handle_edit_fact, name="edit_fact")
    mcp.tool(tools.handle_delete_fact, name="delete_fact")
