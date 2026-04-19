def build_bash_command_with_cmdmeta(bare: str, *, tools: tuple[str, ...] = (), endpoints: tuple[str, ...] = (), flags: tuple[str, ...] = (), affected_paths: tuple[str, ...] = ()) -> str:
    """Build a full Bash ``tool_input.command`` string with a trailing CMD-META block.

    Test helper — keeps integration scenarios readable by separating the bare
    command from its manifest fields instead of inlining multi-line strings.

    Args:
        bare: Everything before the META trailer (e.g. ``"git push origin main"``).
        tools: Values for the required ``tools:`` key. Empty tuple still emits
            ``"# tools:"`` — the key is required even when empty.
        endpoints: Values for the optional ``endpoints:`` key. Omitted when empty.
        flags: Values for the optional ``flags:`` key. Omitted when empty.
        affected_paths: Values for the optional ``affected_paths:`` key. Omitted
            when empty.

    Returns:
        The full command string including BEGIN/END sentinels, ready to place
        in ``tool_input.command`` on a Bash PreToolUse event.
    """
    lines = ["# ---CMD-META-BEGIN---", f"# tools: {', '.join(tools)}"]
    if endpoints:
        lines.append(f"# endpoints: {', '.join(endpoints)}")
    if flags:
        lines.append(f"# flags: {', '.join(flags)}")
    if affected_paths:
        lines.append(f"# affected_paths: {', '.join(affected_paths)}")
    lines.append("# ---CMD-META-END---")

    return bare + "  " + "\n".join(lines)
