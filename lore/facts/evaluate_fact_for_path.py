import re

from lore.facts.fact import Fact
from lore.facts.matcher_set import MatcherSet
from lore.matchers.match_path_to_glob import match_path_to_glob


def evaluate_fact_for_path(
    fact: Fact,
    path: str,
    content: str | None = None,
    description: str | None = None,
    command: str | None = None,
) -> bool:
    """Test if a tool event matches a typed Fact.

    Within each MatcherSet, matchers of the same target OR together,
    and groups of different targets AND together. An empty group is
    vacuously true.

    Per Decision 10 (see command-hooks-plan.md): when a group has
    matchers but the event provides no source for them (e.g. a `d:`
    matcher on a file Edit event), the group evaluates to False.

    Skip fires only when every one of its non-empty groups matches.

    Args:
        fact: Typed Fact with compiled MatcherSets.
        path: Path to test (use trailing / for directories).
            Pass empty string for events without a path.
        content: Optional content to test content regexes against.
        description: Optional description text to test description regexes against.
        command: Optional raw command text to test command regexes against.

    Returns:
        True if the event matches the fact, False otherwise.
    """
    if _has_matchers(fact.skip) and _matches_matcher_set(fact.skip, path, content, description, command):
        return False

    return _matches_matcher_set(fact.incl, path, content, description, command)


def _has_matchers(matcher_set: MatcherSet) -> bool:
    """Check if a MatcherSet contains any matchers at all."""
    return bool(
        matcher_set.path_globs
        or matcher_set.content_regexes
        or matcher_set.description_regexes
        or matcher_set.command_regexes
    )


def _matches_matcher_set(
    matcher_set: MatcherSet,
    path: str,
    content: str | None,
    description: str | None,
    command: str | None,
) -> bool:
    """Check if an event matches a MatcherSet."""
    return (
        _check_path_globs(matcher_set.path_globs, path)
        and _check_text_regexes(matcher_set.content_regexes, content)
        and _check_text_regexes(matcher_set.description_regexes, description)
        and _check_text_regexes(matcher_set.command_regexes, command)
    )


def _check_path_globs(globs: tuple[dict, ...], path: str) -> bool:
    """Check if any glob matches. Empty group = vacuously true."""
    if not globs:
        return True
    if not path:
        return False
    return any(match_path_to_glob(g, path) for g in globs)


def _check_text_regexes(regexes: tuple[re.Pattern, ...], text: str | None) -> bool:
    """Check if any regex matches. Empty group = vacuously true.

    If text is None and regexes exist, returns False (no source to check).
    """
    if not regexes:
        return True
    if text is None:
        return False
    return any(r.search(text) for r in regexes)
