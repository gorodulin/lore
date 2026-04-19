_BEGIN_SENTINEL = "# ---CMD-META-BEGIN---"


def extract_cmdmeta_block(command: str) -> tuple[str, str | None]:
    """Split a command string at the first BEGIN sentinel.

    Locates ``# ---CMD-META-BEGIN---`` and returns everything before it
    (with any trailing whitespace trimmed) as the bare command, and
    everything after it — including the END sentinel if present — as
    the block text.

    Detecting and consuming the END sentinel, and validating the block
    body, are the parser's responsibilities. This function only performs
    the cheap ``find``-based split so callers like the collector can
    obtain a META-free command for ``x:`` matching without paying full
    parse cost.

    Args:
        command: The raw ``tool_input.command`` string.

    Returns:
        ``(bare_command, post_begin_text)``. When no BEGIN sentinel is
        present, returns ``(command, None)``.
    """
    begin_idx = command.find(_BEGIN_SENTINEL)
    if begin_idx == -1:
        return command, None

    bare_end = begin_idx
    while bare_end > 0 and command[bare_end - 1] in " \t":
        bare_end -= 1
    bare_command = command[:bare_end]

    after_begin = begin_idx + len(_BEGIN_SENTINEL)
    post_begin_text = command[after_begin:]
    if post_begin_text.startswith("\n"):
        post_begin_text = post_begin_text[1:]

    return bare_command, post_begin_text
