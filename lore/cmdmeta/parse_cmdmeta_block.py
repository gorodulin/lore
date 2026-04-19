from lore.cmdmeta.cmdmeta import CmdMeta


_END_SENTINEL = "# ---CMD-META-END---"
_BEGIN_SENTINEL = "# ---CMD-META-BEGIN---"
_KNOWN_KEYS: frozenset[str] = frozenset({"tools", "endpoints", "flags", "affected_paths"})


class CmdMetaParseError(Exception):
    """Raised when a CMD-META block is structurally malformed."""


def parse_cmdmeta_block(post_begin_text: str) -> CmdMeta:
    """Parse the text following a BEGIN sentinel into a typed CmdMeta.

    Handles END-sentinel detection, line-level parsing, key validation,
    and required-field checks. Raises ``CmdMetaParseError`` on any
    structural problem.

    Args:
        post_begin_text: Text that follows the BEGIN sentinel, as
            returned by :func:`extract_cmdmeta_block`. Must still contain
            the END sentinel somewhere inside.

    Returns:
        A :class:`CmdMeta` with ``tools`` / ``endpoints`` / ``flags`` /
        ``affected_paths`` filled from the block. Keys omitted from the
        block stay at their default empty tuple.

    Raises:
        CmdMetaParseError: END sentinel missing, non-whitespace content
            follows the END sentinel, a second BEGIN sentinel appears
            inside the block, any line is not a ``# <key>: <values>``
            comment, a key is unknown, or the required ``tools:`` key
            is missing.
    """
    end_idx = post_begin_text.find(_END_SENTINEL)
    if end_idx == -1:
        raise CmdMetaParseError("END sentinel '# ---CMD-META-END---' missing")

    tail = post_begin_text[end_idx + len(_END_SENTINEL):]
    if tail.strip():
        raise CmdMetaParseError(
            "unexpected content after END sentinel: "
            f"{tail.strip()[:60]!r}"
        )

    block_body = post_begin_text[:end_idx]

    if _BEGIN_SENTINEL in block_body:
        raise CmdMetaParseError("second BEGIN sentinel inside CMD-META block")

    fields: dict[str, tuple[str, ...]] = {}

    for raw_line in block_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not line.startswith("#"):
            raise CmdMetaParseError(
                f"line does not start with '#': {raw_line!r}"
            )
        content = line[1:].lstrip()
        if ":" not in content:
            raise CmdMetaParseError(
                f"missing ':' in CMD-META line: {raw_line!r}"
            )
        key, _, values_str = content.partition(":")
        key = key.strip()
        if key not in _KNOWN_KEYS:
            raise CmdMetaParseError(
                f"unknown CMD-META key {key!r}; expected one of "
                f"{sorted(_KNOWN_KEYS)}"
            )
        if key in fields:
            raise CmdMetaParseError(f"duplicate CMD-META key {key!r}")
        fields[key] = _split_values(values_str)

    if "tools" not in fields:
        raise CmdMetaParseError("required CMD-META key 'tools' is missing")

    return CmdMeta(
        tools=fields.get("tools", ()),
        endpoints=fields.get("endpoints", ()),
        flags=fields.get("flags", ()),
        affected_paths=fields.get("affected_paths", ()),
    )


def _split_values(raw: str) -> tuple[str, ...]:
    """Split a comma-separated values string into a trimmed tuple.

    Whitespace is trimmed; empty entries (e.g. from ``a, , b``) are
    retained as empty strings so the validator can surface them as
    errors. A wholly empty input (``# tools:``) yields ``()`` — the
    grammar allows empty value lists for keys whose presence is required
    but whose content doesn't apply.
    """
    stripped = raw.strip()
    if not stripped:
        return ()
    return tuple(part.strip() for part in raw.split(","))
