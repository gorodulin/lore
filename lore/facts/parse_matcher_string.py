# Valid matcher type prefixes
VALID_PREFIXES = {"g": "glob", "r": "regex", "s": "string"}


def parse_matcher_string(matcher: str) -> tuple[str, str]:
    """Parse a prefixed matcher string into its type and value.

    Matchers use a prefix to indicate their type:
    - "g:" for glob patterns
    - "r:" for regular expressions (future)
    - "s:" for literal strings (future)

    Args:
        matcher: Prefixed matcher string (e.g., "g:**/*.js")

    Returns:
        Tuple of (matcher_type, value) where matcher_type is one of
        "glob", "regex", "string"

    Raises:
        ValueError: If matcher has no prefix or invalid prefix

    Examples:
        >>> parse_matcher_string("g:**/*.js")
        ('glob', '**/*.js')
        >>> parse_matcher_string("g:src/")
        ('glob', 'src/')
    """
    if not matcher or len(matcher) < 3:
        raise ValueError(f"Invalid matcher format: {matcher!r}")

    if matcher[1] != ":":
        raise ValueError(f"Matcher must have prefix (e.g., 'g:'): {matcher!r}")

    prefix = matcher[0]
    value = matcher[2:]

    if prefix not in VALID_PREFIXES:
        valid = ", ".join(f"'{p}:'" for p in sorted(VALID_PREFIXES.keys()))
        raise ValueError(f"Invalid matcher prefix '{prefix}:'. Valid prefixes: {valid}")

    if not value:
        raise ValueError(f"Matcher value cannot be empty: {matcher!r}")

    return VALID_PREFIXES[prefix], value
