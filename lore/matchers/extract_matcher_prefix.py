from lore.facts.parse_matcher_string import parse_matcher_string
from lore.globs.compile_glob_pattern import compile_glob_pattern
from lore.globs.extract_glob_fixed_prefix import extract_glob_fixed_prefix


def extract_matcher_prefix(matcher: str) -> list[str] | None:
    """Extract the literal path prefix segments from a matcher string.

    For glob matchers, parses the pattern and extracts fixed prefix segments.
    Returns None for non-glob matchers or invalid patterns.

    Example:
        >>> extract_matcher_prefix("g:src/api/**/*.ts")
        ["src", "api"]
        >>> extract_matcher_prefix("g:**/*.ts")
        []
        >>> extract_matcher_prefix("r:import os")
        None
    """
    try:
        matcher_type, value = parse_matcher_string(matcher)
    except ValueError:
        return None

    if matcher_type != "glob":
        return None

    try:
        compiled = compile_glob_pattern(value)
        if not compiled.get("valid"):
            return None
        return extract_glob_fixed_prefix(compiled)
    except Exception:
        return None
