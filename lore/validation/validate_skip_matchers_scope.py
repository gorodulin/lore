from lore.matchers.extract_matcher_prefix import extract_matcher_prefix
from lore.paths.check_prefix_overlap import check_prefix_overlap


def validate_skip_matchers_scope(incl: list[str], skip: list[str]) -> list[tuple[str, str]]:
    """Check if skip patterns are within the scope of incl patterns.

    Analyzes patterns in project-root format (before relativization) to determine
    if skip patterns could actually exclude paths matched by incl patterns.

    A skip pattern is "out of scope" if its literal path prefix doesn't overlap
    with any incl pattern's literal path prefix, meaning it can never exclude
    any paths that incl would match.

    Args:
        incl: List of inclusion patterns in project-root format (e.g., ["p:src/api/**/*.ts"])
        skip: List of skip patterns in project-root format (e.g., ["p:vendor/**"])

    Returns:
        List of (skip_pattern, reason) tuples for patterns out of scope.
        Empty list means all skip patterns are potentially useful.

    Example:
        >>> validate_skip_matchers_scope(
        ...     incl=["p:src/api/**/*.ts"],
        ...     skip=["p:vendor/**", "p:src/**/*.test.ts"]
        ... )
        [("p:vendor/**", "does not overlap with any inclusion pattern")]
    """
    if not skip:
        return []

    results = []

    for skip_pattern in skip:
        skip_prefix = extract_matcher_prefix(skip_pattern)
        if skip_prefix is None:
            continue

        is_in_scope = False
        for incl_pattern in incl:
            incl_prefix = extract_matcher_prefix(incl_pattern)
            if incl_prefix is None:
                is_in_scope = True
                break

            if check_prefix_overlap(skip_prefix, incl_prefix):
                is_in_scope = True
                break

        if not is_in_scope:
            results.append((
                skip_pattern,
                "does not overlap with any inclusion pattern"
            ))

    return results
