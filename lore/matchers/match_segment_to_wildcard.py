def match_segment_to_wildcard(wildcard: str, segment: str) -> bool:
    """Match a single path segment against a '*' wildcard pattern.

    The wildcard may contain at most one '*' which matches any characters.

    Args:
        wildcard: Wildcard pattern, may contain one '*' (e.g., "*.ts", "test_*", "f*o")
        segment: Path segment to match against

    Returns:
        True if segment matches the wildcard

    Examples:
        ("*.ts", "file.ts") -> True
        ("*.ts", "file.js") -> False
        ("test_*", "test_foo") -> True
        ("f*o", "foo") -> True
        ("f*o", "foooo") -> True
        ("file.ts", "file.ts") -> True (literal match)
    """
    if "*" not in wildcard:
        return wildcard == segment

    star_pos = wildcard.index("*")
    prefix = wildcard[:star_pos]
    suffix = wildcard[star_pos + 1:]

    # Check prefix
    if not segment.startswith(prefix):
        return False

    # Check suffix
    if not segment.endswith(suffix):
        return False

    # Ensure prefix and suffix don't overlap
    # e.g., wildcard "ab*ba" should not match "aba" (prefix "ab", suffix "ba" overlap)
    if len(prefix) + len(suffix) > len(segment):
        return False

    return True
