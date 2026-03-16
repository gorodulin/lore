from lore.facts.parse_matcher_string import VALID_PREFIXES

_TYPE_TO_PREFIX = {v: k for k, v in VALID_PREFIXES.items()}


def build_matcher_string(matcher_type: str, value: str) -> str:
    """Build a prefixed matcher string from type and value.

    Inverse of parse_matcher_string.

    Args:
        matcher_type: One of "glob", "regex", "string"
        value: Raw pattern value (e.g., "**/*.py")

    Returns:
        Prefixed matcher string (e.g., "g:**/*.py")

    Raises:
        ValueError: If matcher_type is unknown

    Examples:
        >>> build_matcher_string("glob", "**/*.py")
        'g:**/*.py'
        >>> build_matcher_string("regex", "import os")
        'r:import os'
    """
    prefix = _TYPE_TO_PREFIX.get(matcher_type)
    if prefix is None:
        valid = ", ".join(sorted(_TYPE_TO_PREFIX.keys()))
        raise ValueError(f"Unknown matcher type '{matcher_type}'. Valid types: {valid}")
    return f"{prefix}:{value}"
