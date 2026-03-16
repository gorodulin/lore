import sys

from fastmcp import FastMCP

from lore.mcp.register_mcp_tools import register_mcp_tools
from lore.paths.resolve_project_root import resolve_project_root


_INSTRUCTIONS = """\
lore stores **facts** - short reminders about codebase conventions, \
attached to files via patterns. They capture wisdom linters can't enforce: \
architectural boundaries, naming rules, design commitments, workflow tips. \
Facts fire automatically when matching files are touched, preventing \
conventions from silently drifting.

Each fact has:
- **fact**: short, actionable reminder text
- **incl**: match patterns - "g:<glob>" for paths, "r:<regex>" for file \
content. ALL must match. Combine glob+regex to scope precisely.
- **skip** (optional): exclusion patterns (same syntax). Any match excludes \
the file.
- **tags** (optional): metadata

Tools: `find_facts` (check conventions for a file), `create_fact` (record \
new), `read_fact`/`edit_fact`/`delete_fact` (manage existing).

**Be proactive**: as you work, watch for conventions worth preserving as \
facts. Propose fact text + patterns to the user; always discuss before \
creating."""


def serve_mcp():
    """Start the lore MCP server over stdio."""
    project_root = resolve_project_root(sys.argv[1] if len(sys.argv) > 1 else None)

    mcp = FastMCP("lore", instructions=_INSTRUCTIONS)
    register_mcp_tools(mcp, project_root)
    mcp.run()


if __name__ == "__main__":
    serve_mcp()
