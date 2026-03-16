"""
Handle Claude Code hook events for lore.

Reads a hook event JSON from stdin, dispatches it through the handler
pipeline, and writes a response JSON to stdout.

Usage (called via bin/handle_claude_hook wrapper):
    echo '{"hook_event_name":"PostToolUse","tool_name":"Read",...}' | \
        bin/handle_claude_hook
"""

import json
import os
import sys

from lore.claude.dispatch_hook_event import dispatch_hook_event


def handle_claude_hook():
    raw = sys.stdin.read().strip()
    if not raw:
        print("{}")
        return

    try:
        event_data = json.loads(raw)
    except json.JSONDecodeError:
        print("{}")
        return

    project_root = (
        os.environ.get("CLAUDE_PROJECT_ROOT", "")
        or event_data.get("cwd", "")
    )

    log_path = os.environ.get("LORE_LOG", "")

    result = dispatch_hook_event(
        event_data, project_root=project_root, log_path=log_path
    )

    print(json.dumps(result))


if __name__ == "__main__":
    handle_claude_hook()
