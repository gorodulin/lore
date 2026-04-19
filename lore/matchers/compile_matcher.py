import re

from lore.globs.compile_glob_pattern import compile_glob_pattern


def compile_matcher(matcher_type: str, value: str):
    """Compile a single matcher value into its executable form.

    Args:
        matcher_type: One of "path", "content", "description", "command", "tool"
        value: Raw value (e.g., glob pattern "**/*.py" or regex "import os")

    Returns:
        Compiled glob dict (for "path") or re.Pattern (for regex-based types).

    Raises:
        ValueError: If matcher_type is unknown
    """
    if matcher_type == "path":
        return compile_glob_pattern(value)
    elif matcher_type in {"content", "description", "command", "tool"}:
        return re.compile(value, re.MULTILINE)
    else:
        raise ValueError(f"Unknown matcher type: {matcher_type}")
