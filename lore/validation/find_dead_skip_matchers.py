from lore.matchers.extract_matcher_prefix import extract_matcher_prefix
from lore.paths.check_prefix_overlap import check_prefix_overlap


def find_dead_skip_matchers(fact: dict) -> list[str]:
    """Find negative matchers that cannot exclude anything.

    A negative matcher is "dead" if it cannot possibly exclude any path
    that would be matched by the positive matchers. This happens when
    the negative's fixed prefix doesn't overlap with any positive's
    fixed prefix.

    This is a heuristic check - it may miss some dead negatives with
    complex patterns, but won't report false positives.

    Args:
        fact: Fact dict with 'incl' and optional 'skip' lists

    Returns:
        List of negative matchers that appear to be dead.

    Example:
        >>> find_dead_skip_matchers({
        ...     'fact': 'Test',
        ...     'incl': ['p:src/**/*.js'],
        ...     'skip': ['p:vendor/**'],  # can never match src/** paths
        ... })
        ['p:vendor/**']
    """
    incl = fact.get("incl", [])
    skip = fact.get("skip", [])

    if not skip:
        return []

    positive_prefixes = []
    for matcher in incl:
        prefix = extract_matcher_prefix(matcher)
        if prefix is not None:
            positive_prefixes.append(prefix)

    if not positive_prefixes:
        return []

    dead = []
    for matcher in skip:
        negative_prefix = extract_matcher_prefix(matcher)
        if negative_prefix is None:
            continue

        if not _any_prefix_overlaps(negative_prefix, positive_prefixes):
            dead.append(matcher)

    return dead


def _any_prefix_overlaps(prefix: list[str], candidates: list[list[str]]) -> bool:
    """Check if prefix overlaps with any candidate prefix."""
    for candidate in candidates:
        if check_prefix_overlap(prefix, candidate):
            return True
    return False
