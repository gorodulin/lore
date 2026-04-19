import re

from lore.facts.fact import Fact
from lore.facts.matcher_set import MatcherSet
from lore.matchers.match_path_to_glob import match_path_to_glob


def evaluate_fact_for_path(fact: Fact, path: str, content: str | None = None, description: str | None = None, command: str | None = None, tools: tuple[str, ...] | None = None, endpoints: tuple[str, ...] | None = None, flags: tuple[str, ...] | None = None, affected_paths: tuple[str, ...] | None = None) -> bool:
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
        tools: Optional per-item tool entries from CMD-META. Each ``t:``
            regex is tested against every entry; the group matches if
            any entry matches any regex.
        endpoints: Optional per-item endpoint entries. Source: CMD-META
            endpoints on Bash events, ``(tool_input.url,)`` on WebFetch.
        flags: Optional per-item flag literals from CMD-META. Each ``f:``
            entry is tested for exact membership; the group matches if
            any fact entry appears in the event's flags.
        affected_paths: Optional per-item path source for ``p:`` matchers
            on Bash events (from ``meta.affected_paths``). When supplied,
            it overrides the single ``path`` argument: each glob is tested
            against every affected path. Per decision 5, the same ``p:``
            matcher serves both file events (single ``path``) and Bash
            events (multi-item ``affected_paths``).

    Returns:
        True if the event matches the fact, False otherwise.
    """
    if _has_matchers(fact.skip) and _matches_matcher_set(fact.skip, path, content, description, command, tools, endpoints, flags, affected_paths):
        return False

    return _matches_matcher_set(fact.incl, path, content, description, command, tools, endpoints, flags, affected_paths)


def _has_matchers(matcher_set: MatcherSet) -> bool:
    """Check if a MatcherSet contains any matchers at all."""
    return bool(
        matcher_set.path_globs
        or matcher_set.content_regexes
        or matcher_set.description_regexes
        or matcher_set.command_regexes
        or matcher_set.tool_regexes
        or matcher_set.endpoint_regexes
        or matcher_set.flag_literals
    )


def _matches_matcher_set(matcher_set: MatcherSet, path: str, content: str | None, description: str | None, command: str | None, tools: tuple[str, ...] | None, endpoints: tuple[str, ...] | None, flags: tuple[str, ...] | None, affected_paths: tuple[str, ...] | None) -> bool:
    """Check if an event matches a MatcherSet."""
    return (
        _check_path_globs(matcher_set.path_globs, path, affected_paths)
        and _check_text_regexes(matcher_set.content_regexes, content)
        and _check_text_regexes(matcher_set.description_regexes, description)
        and _check_text_regexes(matcher_set.command_regexes, command)
        and _check_any_regex_in_items(matcher_set.tool_regexes, tools)
        and _check_any_regex_in_items(matcher_set.endpoint_regexes, endpoints)
        and _check_any_literal_in_items(matcher_set.flag_literals, flags)
    )


def _check_path_globs(globs: tuple[dict, ...], path: str, affected_paths: tuple[str, ...] | None = None) -> bool:
    """Check if any glob matches the event's path source.

    Per decision 5, ``p:`` serves both file events (single ``path``) and
    Bash events (multi-item ``affected_paths`` from CMD-META). When
    ``affected_paths`` is not None, it takes priority — each glob is
    tested against every affected path. Otherwise falls back to the
    single-path behavior used by file events.

    Empty globs group is vacuously true. Missing source (empty ``path``
    when ``affected_paths is None``, or empty ``affected_paths`` tuple)
    yields False when globs are present.
    """
    if not globs:
        return True
    if affected_paths is not None:
        if not affected_paths:
            return False
        return any(match_path_to_glob(g, ap) for g in globs for ap in affected_paths)
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


def _check_any_regex_in_items(regexes: tuple[re.Pattern, ...], items: tuple[str, ...] | None) -> bool:
    """Per-item any-any check: True if any regex matches any item.

    Empty regexes group = vacuously true. ``items is None`` means the
    event type provides no source for this target (decision 10): False.
    Empty items tuple means the source is present but carries nothing,
    so no item can satisfy any regex: also False.
    """
    if not regexes:
        return True
    if items is None:
        return False
    return any(r.search(item) for r in regexes for item in items)


def _check_any_literal_in_items(literals: tuple[str, ...], items: tuple[str, ...] | None) -> bool:
    """Per-item exact-match check: True if any literal equals any item.

    Same empty/None semantics as :func:`_check_any_regex_in_items`, but
    uses set membership instead of regex search — suitable for closed
    vocabularies like CMD-META flags.
    """
    if not literals:
        return True
    if items is None:
        return False
    items_set = frozenset(items)
    return any(literal in items_set for literal in literals)
