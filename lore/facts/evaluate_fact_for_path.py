from lore.matchers.match_path_to_glob import match_path_to_glob


def evaluate_fact_for_path(compiled_fact: dict, path: str, content: str | None = None) -> bool:
    """Test if a path (and optionally content) matches a compiled fact.

    Matchers are split into two groups:
    - Path matchers (glob/string): OR within group
    - Content matchers (regex): OR within group
    - AND between the two groups

    A match requires both groups to match (empty group = vacuously true).

    Skip matchers use the same AND logic: skip fires only when both
    path and content groups match.

    Args:
        compiled_fact: Compiled fact from compile_fact_matchers()
        path: Path to test (use trailing / for directories)
        content: Optional content to test regex matchers against

    Returns:
        True if path/content matches the fact, False otherwise
    """
    # Split skip matchers and check - only apply when skip has matchers
    skip_matchers = compiled_fact.get("skip", [])
    if skip_matchers:
        skip_path = [(o, m) for o, m in skip_matchers if _is_path_matcher(m)]
        skip_content = [(o, m) for o, m in skip_matchers if _is_content_matcher(m)]

        skip_matches = (
            _check_path_group(skip_path, path)
            and _check_content_group(skip_content, content)
        )
        if skip_matches:
            return False

    # Split incl matchers and check
    incl_matchers = compiled_fact.get("incl", [])
    incl_path = [(o, m) for o, m in incl_matchers if _is_path_matcher(m)]
    incl_content = [(o, m) for o, m in incl_matchers if _is_content_matcher(m)]

    return (
        _check_path_group(incl_path, path)
        and _check_content_group(incl_content, content)
    )


def _is_path_matcher(compiled: dict) -> bool:
    """Check if a compiled matcher is a path matcher (glob/string)."""
    return "segments" in compiled


def _is_content_matcher(compiled: dict) -> bool:
    """Check if a compiled matcher is a content matcher (regex)."""
    return "regex" in compiled


def _check_path_group(matchers: list, path: str) -> bool:
    """Check if any path matcher matches. Empty group = vacuously true."""
    if not matchers:
        return True
    return any(match_path_to_glob(m, path) for _o, m in matchers)


def _check_content_group(matchers: list, content: str | None) -> bool:
    """Check if any content matcher matches. Empty group = vacuously true.

    If content is None and matchers exist, returns False (can't verify).
    """
    if not matchers:
        return True
    if content is None:
        return False
    return any(m["regex"].search(content) for _o, m in matchers)
