import re

from lore.facts.fact import Fact
from lore.facts.matcher_set import MatcherSet
from lore.matchers.match_path_to_glob import match_path_to_glob


def evaluate_fact_for_path(fact: Fact, path: str, content: str | None = None) -> bool:
    """Test if a path (and optionally content) matches a typed Fact.

    Within each MatcherSet, path globs OR together and content regexes
    OR together, then the two groups AND. Empty group = vacuously true.

    Skip fires only when both its path and content groups match.

    Args:
        fact: Typed Fact with compiled MatcherSets.
        path: Path to test (use trailing / for directories).
        content: Optional content to test regex matchers against.

    Returns:
        True if path/content matches the fact, False otherwise.
    """
    if _has_matchers(fact.skip) and _matches_matcher_set(fact.skip, path, content):
        return False

    return _matches_matcher_set(fact.incl, path, content)


def _has_matchers(matcher_set: MatcherSet) -> bool:
    """Check if a MatcherSet contains any matchers at all."""
    return bool(matcher_set.path_globs or matcher_set.content_regexes)


def _matches_matcher_set(matcher_set: MatcherSet, path: str, content: str | None) -> bool:
    """Check if a path/content pair matches a MatcherSet."""
    return (
        _check_path_globs(matcher_set.path_globs, path)
        and _check_content_regexes(matcher_set.content_regexes, content)
    )


def _check_path_globs(globs: tuple[dict, ...], path: str) -> bool:
    """Check if any glob matches. Empty group = vacuously true."""
    if not globs:
        return True
    return any(match_path_to_glob(g, path) for g in globs)


def _check_content_regexes(regexes: tuple[re.Pattern, ...], content: str | None) -> bool:
    """Check if any regex matches. Empty group = vacuously true.

    If content is None and regexes exist, returns False (can't verify).
    """
    if not regexes:
        return True
    if content is None:
        return False
    return any(r.search(content) for r in regexes)
