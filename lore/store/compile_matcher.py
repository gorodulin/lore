import re

from lore.globs.compile_glob_pattern import compile_glob_pattern


def compile_matcher(matcher_type: str, value: str):
    """Compile a single matcher value into its executable form.

    Args:
        matcher_type: One of "glob", "regex"
        value: Raw pattern value (e.g., "**/*.py" or "import os")

    Returns:
        Compiled glob dict (for "glob") or re.Pattern (for "regex")

    Raises:
        ValueError: If matcher_type is unknown
    """
    if matcher_type == "glob":
        return compile_glob_pattern(value)
    elif matcher_type == "regex":
        return re.compile(value, re.MULTILINE)
    else:
        raise ValueError(f"Unknown matcher type: {matcher_type}")
