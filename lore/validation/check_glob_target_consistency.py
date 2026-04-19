from lore.store.parse_matcher_string import parse_matcher_string
from lore.globs.compile_glob_pattern import compile_glob_pattern


def check_glob_target_consistency(fact: dict) -> dict | None:
    """Check if all glob matchers in a fact target the same type (files or dirs).

    All globs within a fact should target either files OR directories,
    not both. This prevents undefined semantics and accidental matches.

    A glob targets directories if it ends with '/'.
    A glob targets files if it doesn't end with '/'.

    Args:
        fact: Fact dict with 'incl' and optional 'skip' lists

    Returns:
        None if consistent, or a dict with issue details:
        {
            'file_globs': [...],   # globs targeting files
            'dir_globs': [...],    # globs targeting directories
        }

    Example:
        >>> check_glob_target_consistency({
        ...     'fact': 'Mixed targets',
        ...     'incl': ['p:**/*.js', 'p:src/'],
        ... })
        {'file_globs': ['p:**/*.js'], 'dir_globs': ['p:src/']}
    """
    file_globs = []
    dir_globs = []

    all_matchers = []
    all_matchers.extend(fact.get("incl", []))
    all_matchers.extend(fact.get("skip", []))

    for matcher in all_matchers:
        target = _get_glob_target(matcher)
        if target == "file":
            file_globs.append(matcher)
        elif target == "dir":
            dir_globs.append(matcher)
        # Non-glob matchers are ignored

    # Consistent if all are same type or one list is empty
    if file_globs and dir_globs:
        return {
            "file_globs": file_globs,
            "dir_globs": dir_globs,
        }

    return None



def _get_glob_target(matcher: str) -> str | None:
    """Determine if a glob targets files or directories.

    Returns 'file', 'dir', or None (not a glob / can't determine).
    """
    try:
        matcher_type, value = parse_matcher_string(matcher)
    except ValueError:
        return None

    if matcher_type != "path":
        return None

    try:
        compiled = compile_glob_pattern(value)
        if not compiled.get("valid"):
            return None

        if compiled.get("is_dir"):
            return "dir"
        return "file"
    except Exception:
        return None
