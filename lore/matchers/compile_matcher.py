import re

from lore.globs.compile_glob_pattern import compile_glob_pattern


def compile_matcher(matcher_type: str, value: str):
    """Compile a single matcher value into its executable form.

    Args:
        matcher_type: One of "path", "content", "description", "command",
            "tool", "endpoint", "flag"
        value: Raw value (e.g., glob pattern "**/*.py", regex "import os",
            or a flag literal like "mutates")

    Returns:
        Compiled glob dict (for "path"), re.Pattern (for regex-based types),
        or the raw string (for "flag" — exact-match literal).

    Raises:
        ValueError: If matcher_type is unknown
    """
    if matcher_type == "path":
        return compile_glob_pattern(value)
    elif matcher_type in {"content", "description", "command", "tool", "endpoint"}:
        return re.compile(value, re.MULTILINE)
    elif matcher_type == "flag":
        return value
    else:
        raise ValueError(f"Unknown matcher type: {matcher_type}")
