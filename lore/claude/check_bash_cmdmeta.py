from lore.cmdmeta.build_cmdmeta_instruction import build_cmdmeta_instruction
from lore.cmdmeta.resolve_cmdmeta_for_command import resolve_cmdmeta_for_command


def check_bash_cmdmeta(event_data: dict, *, project_root: str, log_path: str, hook_tag: str | None = None, display_rate: int = 1) -> dict:
    """Gate Bash PreToolUse events on presence of a valid CMD-META block.

    Delegates the extract → parse → validate pipeline to
    :func:`resolve_cmdmeta_for_command` (shared with the fact collector).
    Any failure short-circuits to a ``permissionDecision: "deny"`` payload
    whose reason is composed by :func:`build_cmdmeta_instruction`.

    Registered directly in ``HANDLERS`` — the kwargs
    ``project_root`` / ``log_path`` / ``hook_tag`` / ``display_rate``
    are part of the dispatch contract and are intentionally unused here.
    """
    del project_root, log_path, hook_tag, display_rate

    tool_input = event_data.get("tool_input", {})
    command = tool_input.get("command", "")

    resolution = resolve_cmdmeta_for_command(command)

    if not resolution.block_present:
        return _deny_response(("CMD-META block missing — no BEGIN sentinel found",))

    if resolution.errors:
        return _deny_response(resolution.errors)

    return {}


def _deny_response(errors: tuple[str, ...]) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": build_cmdmeta_instruction(errors),
        }
    }
