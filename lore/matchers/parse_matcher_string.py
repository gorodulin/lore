# Valid matcher type prefixes. Types are target-named (not strategy-named):
# each target maps 1:1 to a prefix letter.
VALID_PREFIXES = {
    "p": "path",
    "c": "content",
    "d": "description",
    "x": "command",
    "t": "tool",
    "s": "string",
}


def parse_matcher_string(matcher: str) -> tuple[str, str]:
    """Parse a prefixed matcher string into its type and value.

    Matchers use a prefix to indicate their target:
    - "p:" for path globs
    - "c:" for content regexes
    - "d:" for description regexes
    - "x:" for raw command regexes
    - "t:" for tool-entry regexes (per-item against CMD-META tools)
    - "s:" for literal strings (future)

    Args:
        matcher: Prefixed matcher string (e.g., "p:**/*.js")

    Returns:
        Tuple of (matcher_type, value) where matcher_type is one of
        "path", "content", "description", "command", "tool", "string".

    Raises:
        ValueError: If matcher has no prefix or invalid prefix

    Examples:
        >>> parse_matcher_string("p:**/*.js")
        ('path', '**/*.js')
        >>> parse_matcher_string("c:import os")
        ('content', 'import os')
        >>> parse_matcher_string("d:(?i)deploy")
        ('description', '(?i)deploy')
        >>> parse_matcher_string("t:git push")
        ('tool', 'git push')
    """
    if not matcher or len(matcher) < 3:
        raise ValueError(f"Invalid matcher format: {matcher!r}")

    if matcher[1] != ":":
        raise ValueError(f"Matcher must have prefix (e.g., 'p:'): {matcher!r}")

    prefix = matcher[0]
    value = matcher[2:]

    if prefix not in VALID_PREFIXES:
        valid = ", ".join(f"'{p}:'" for p in sorted(VALID_PREFIXES.keys()))
        raise ValueError(f"Invalid matcher prefix '{prefix}:'. Valid prefixes: {valid}")

    if not value:
        raise ValueError(f"Matcher value cannot be empty: {matcher!r}")

    return VALID_PREFIXES[prefix], value
