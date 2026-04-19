import sys
import traceback

from lore.claude.log_hook_event import log_hook_event
from lore.claude.collect_facts_for_tool_event import collect_facts_for_tool_event
from lore.claude.check_bash_cmdmeta import check_bash_cmdmeta


HANDLERS = [
    ("*", None, None, log_hook_event, 1),
    ("PostToolUse", "Read", "hook:read", collect_facts_for_tool_event, 5),
    ("PreToolUse", "Edit", "hook:edit", collect_facts_for_tool_event, 1),
    ("PreToolUse", "Write", "hook:write", collect_facts_for_tool_event, 1),
    ("PreToolUse", "Bash", None, check_bash_cmdmeta, 1),
    ("PreToolUse", "Bash", "hook:bash", collect_facts_for_tool_event, 1),
    ("PreToolUse", "Task", "hook:agent", collect_facts_for_tool_event, 1),
    ("PreToolUse", "WebFetch", "hook:webfetch", collect_facts_for_tool_event, 1),
    ("PreToolUse", "WebSearch", "hook:websearch", collect_facts_for_tool_event, 1),
]

"""Registry of hook handlers.

Each entry is ``(event_pattern, tool_pattern | None, hook_tag | None,
handler_fn, display_rate)``.

* ``"*"`` event_pattern matches every event.
* ``None`` tool_pattern matches any tool (or events without a tool).
* ``hook_tag`` is passed to handlers as a kwarg for tag-based filtering.
* ``display_rate`` controls per-session dedup (1 = always show).
* Handler signature: ``(event_data, *, project_root, log_path, hook_tag, display_rate) -> dict | None``
"""


def dispatch_hook_event(event_data: dict, *, project_root: str, log_path: str) -> dict:
    """Dispatch a hook event to all matching handlers and merge results.

    Iterates through HANDLERS, checks whether the event matches each
    handler's pattern, invokes matching handlers, and merges any
    ``additionalContext`` values returned.

    Args:
        event_data: Raw hook event dict from stdin
        project_root: Absolute path to the project root
        log_path: Absolute path to the JSONL log file

    Returns:
        Merged response dict (may be empty ``{}``).
    """
    event_name = event_data.get("hook_event_name", "")
    tool_name = event_data.get("tool_name", "")

    merged = {}

    for event_pattern, tool_pattern, hook_tag, handler_fn, display_rate in HANDLERS:
        if not _matches(event_name, tool_name, event_pattern, tool_pattern):
            continue

        try:
            result = handler_fn(
                event_data, project_root=project_root, log_path=log_path,
                hook_tag=hook_tag, display_rate=display_rate,
            )
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            continue

        if result and isinstance(result, dict):
            _merge_result(merged, result)

    return merged


def _matches(
    event_name: str, tool_name: str, event_pattern: str, tool_pattern: str | None
) -> bool:
    """Check whether an event matches a handler's patterns."""
    if event_pattern != "*" and event_pattern != event_name:
        return False
    if tool_pattern is not None and tool_pattern != tool_name:
        return False
    return True


def _merge_result(merged: dict, result: dict) -> None:
    """Merge a handler result into the accumulated response.

    For ``hookSpecificOutput.additionalContext``, concatenates with newlines.
    Other keys are overwritten (last writer wins).
    """
    for key, value in result.items():
        if key == "hookSpecificOutput" and key in merged:
            _merge_hook_specific_output(merged[key], value)
        else:
            merged[key] = value


def _merge_hook_specific_output(merged: dict, incoming: dict) -> None:
    """Merge hookSpecificOutput dicts, concatenating additionalContext."""
    for key, value in incoming.items():
        if key == "additionalContext" and key in merged:
            merged[key] = merged[key] + "\n" + value
        else:
            merged[key] = value
