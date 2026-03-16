from lore.globs.validate_glob_pattern import validate_glob_pattern
from lore.globs.parse_glob_pattern import parse_glob_pattern


def compile_glob_pattern(glob_pattern: str) -> dict:
    """Validate, parse, and precompute helpers for a glob pattern.

    Args:
        glob_pattern: Glob pattern string

    Returns:
        Dict with:
        - 'raw': original pattern string
        - 'is_dir': True if pattern targets directories
        - 'segments': list of segment tokens
        - 'valid': True if pattern is valid
        - 'errors': list of error dicts (empty if valid)
        - 'globstar_index': index of ** segment, or -1 if none
        - 'fixed_prefix': list of literal segment values before first wildcard

    Raises:
        ValueError if pattern is invalid (use validate_glob_pattern to check first)
    """
    valid, errors = validate_glob_pattern(glob_pattern)

    if not valid:
        return {
            "raw": glob_pattern,
            "is_dir": False,
            "segments": [],
            "valid": False,
            "errors": errors,
            "globstar_index": -1,
            "fixed_prefix": [],
        }

    parsed = parse_glob_pattern(glob_pattern)

    # Find globstar index
    globstar_index = -1
    for i, seg in enumerate(parsed["segments"]):
        if seg["type"] == "globstar":
            globstar_index = i
            break

    # Extract fixed prefix (literal segments before any wildcard)
    fixed_prefix = []
    for seg in parsed["segments"]:
        if seg["type"] == "literal":
            fixed_prefix.append(seg["value"])
        else:
            break

    return {
        "raw": glob_pattern,
        "is_dir": parsed["is_dir"],
        "segments": parsed["segments"],
        "valid": True,
        "errors": [],
        "globstar_index": globstar_index,
        "fixed_prefix": fixed_prefix,
    }
