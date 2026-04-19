from lore.cmdmeta.build_cmdmeta_instruction import build_cmdmeta_instruction
from lore.cmdmeta.extract_cmdmeta_block import extract_cmdmeta_block
from lore.cmdmeta.parse_cmdmeta_block import CmdMetaParseError, parse_cmdmeta_block
from lore.cmdmeta.validate_cmdmeta import validate_cmdmeta


def check_bash_cmdmeta(
    event_data: dict,
    *,
    project_root: str,
    log_path: str,
    hook_tag: str | None = None,
    display_rate: int = 1,
) -> dict:
    """Gate Bash PreToolUse events on presence of a valid CMD-META block.

    Pipeline: :func:`extract_cmdmeta_block` → :func:`parse_cmdmeta_block`
    → :func:`validate_cmdmeta`. Any failure short-circuits to a
    ``permissionDecision: "deny"`` payload whose reason is composed by
    :func:`build_cmdmeta_instruction`.

    Registered directly in ``HANDLERS`` — the kwargs
    ``project_root`` / ``log_path`` / ``hook_tag`` / ``display_rate``
    are part of the dispatch contract and are intentionally unused here.

    Args:
        event_data: Raw hook event dict from stdin.
        project_root: Unused (part of the handler signature).
        log_path: Unused (part of the handler signature).
        hook_tag: Unused (part of the handler signature).
        display_rate: Unused (part of the handler signature).

    Returns:
        ``hookSpecificOutput`` deny payload when META is absent or
        invalid; ``{}`` when a valid META block is present (the
        collector handler runs next and handles fact matching).
    """
    del project_root, log_path, hook_tag, display_rate

    tool_input = event_data.get("tool_input", {})
    command = tool_input.get("command", "")

    _bare_command, block_text = extract_cmdmeta_block(command)

    if block_text is None:
        return _deny_response(("CMD-META block missing — no BEGIN sentinel found",))

    try:
        meta = parse_cmdmeta_block(block_text)
    except CmdMetaParseError as exc:
        return _deny_response((f"CMD-META parse error: {exc}",))

    semantic_errors = validate_cmdmeta(meta)
    if semantic_errors:
        return _deny_response(tuple(semantic_errors))

    return {}


def _deny_response(errors: tuple[str, ...]) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": build_cmdmeta_instruction(errors),
        }
    }
