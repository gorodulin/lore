import os
import sys
import traceback

from lore.claude.match_facts_for_path import match_facts_for_path
from lore.claude.filter_facts_by_hook_tag import filter_facts_by_hook_tag
from lore.claude.filter_facts_by_display_rate import filter_facts_by_display_rate
from lore.facts.build_fact_render_context import build_fact_render_context
from lore.facts.render_fact_text import render_fact_text
from lore.client.try_send_fact_request import try_send_fact_request


def collect_facts_for_tool_event(event_data: dict, *, project_root: str, log_path: str, hook_tag: str | None = None, display_rate: int = 1) -> dict:
    """Extract file_path from a tool event and return matching facts.

    Reads ``tool_input.file_path`` from event_data, runs the matching
    pipeline, filters by hook tag, renders templates, applies display
    rate filtering, and formats the results as
    ``{"additionalContext": "..."}``.

    Returns ``{}`` when there is no file_path or no facts match.

    Args:
        event_data: Raw hook event dict from stdin
        project_root: Absolute path to the project root
        log_path: Path to log file (unused, present for handler signature)
        hook_tag: Hook tag for filtering (e.g. "hook:read"), or None for all
        display_rate: Show every Nth occurrence of identical rendered text
    """
    try:
        tool_input = event_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        if not file_path:
            return {}

        content = _resolve_content(event_data, file_path, project_root)
        facts = _find_facts_via_server(project_root, file_path, content, hook_tag)
        if not facts:
            return {}

        hook_event_name = event_data.get("hook_event_name", "PostToolUse")
        context = build_fact_render_context(file_path, project_root)

        blocking, non_blocking = _separate_blocking_facts(facts)

        if blocking and hook_event_name == "PreToolUse":
            rendered = {fid: render_fact_text(f["fact"], context) for fid, f in blocking.items()}
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": _format_facts(rendered),
                }
            }

        rendered = {fid: render_fact_text(f["fact"], context) for fid, f in facts.items()}

        session_id = event_data.get("session_id", "")
        rendered = filter_facts_by_display_rate(rendered, session_id, display_rate, project_root)
        if not rendered:
            return {}

        return {
            "hookSpecificOutput": {
                "hookEventName": hook_event_name,
                "additionalContext": _format_facts(rendered),
            }
        }
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        return {}


def _find_facts_via_server(project_root: str, file_path: str, content: str | None, hook_tag: str | None) -> dict[str, dict]:
    """Try the lore server first, fall back to in-process matching."""
    params = {"file_path": file_path}
    if content is not None:
        params["content"] = content
    if hook_tag is not None:
        params["tags"] = [hook_tag]
    result = try_send_fact_request(project_root, "find_facts", params)
    if result is not None:
        return result
    # Fallback: in-process
    facts = match_facts_for_path(project_root, file_path, content=content)
    return filter_facts_by_hook_tag(facts, hook_tag)


def _resolve_content(event_data: dict, file_path: str, project_root: str) -> str | None:
    """Determine content to test regex matchers against based on hook type.

    - PreToolUse/Write: tool_input.content (what's being written)
    - PreToolUse/Edit: tool_input.new_string (what's being written)
    - PostToolUse/Read: file body on disk
    """
    hook_event = event_data.get("hook_event_name", "")
    tool_input = event_data.get("tool_input", {})

    if hook_event == "PreToolUse":
        tool_name = event_data.get("tool_name", "")
        if tool_name == "Write":
            return tool_input.get("content")
        if tool_name == "Edit":
            return tool_input.get("new_string")
        return None

    if hook_event == "PostToolUse":
        abs_path = file_path if os.path.isabs(file_path) else os.path.join(project_root, file_path)
        try:
            with open(abs_path) as f:
                return f.read()
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            return None

    return None


def _separate_blocking_facts(facts: dict[str, dict]) -> tuple[dict[str, dict], dict[str, dict]]:
    """Split facts into blocking (action:block tag) and non-blocking.

    Returns:
        Tuple of (blocking, non_blocking) dicts.
    """
    blocking = {}
    non_blocking = {}
    for fid, fact in facts.items():
        if "action:block" in fact.get("tags", []):
            blocking[fid] = fact
        else:
            non_blocking[fid] = fact
    return blocking, non_blocking


def _format_facts(rendered: dict[str, str]) -> str:
    """Format rendered fact texts into tagged strings.

    Example output::

        <F:api-handlers>This module handles API routing</F>
        <F:auth-middleware>Auth is enforced at middleware level</F>
    """
    lines = [f"<F:{fact_id}>{text}</F>" for fact_id, text in rendered.items()]
    return "\n".join(lines)
