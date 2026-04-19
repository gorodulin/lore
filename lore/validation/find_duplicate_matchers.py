def find_duplicate_matchers(fact: dict) -> dict[str, list[str]]:
    """Find duplicate matchers within a single fact.

    Checks both 'incl' and 'skip' lists for matchers that are identical
    after normalization (currently just string comparison).

    Args:
        fact: Fact dict with 'incl' and optional 'skip' lists

    Returns:
        Dict mapping normalized matcher to list of original matchers that
        are duplicates. Only includes entries with 2+ duplicates.

    Example:
        >>> find_duplicate_matchers({
        ...     'fact': 'Test',
        ...     'incl': ['p:**/*.js', 'p:**/*.js', 'p:**/*.ts'],
        ... })
        {'p:**/*.js': ['p:**/*.js', 'p:**/*.js']}
    """
    # Collect all matchers
    all_matchers = []
    all_matchers.extend(fact.get("incl", []))
    all_matchers.extend(fact.get("skip", []))

    # Group by normalized form (currently just the string itself)
    groups: dict[str, list[str]] = {}
    for matcher in all_matchers:
        normalized = _normalize_matcher(matcher)
        if normalized not in groups:
            groups[normalized] = []
        groups[normalized].append(matcher)

    # Return only duplicates
    return {
        normalized: matchers
        for normalized, matchers in groups.items()
        if len(matchers) > 1
    }



def _normalize_matcher(matcher: str) -> str:
    """Normalize a matcher for comparison.

    Currently just returns the string as-is. In future, could:
    - Normalize path separators
    - Collapse redundant patterns
    - Canonicalize regex patterns
    """
    return matcher
