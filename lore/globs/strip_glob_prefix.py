from lore.paths.split_path_segments import split_path_segments
from lore.paths.join_path_segments import join_path_segments
from lore.globs.parse_glob_pattern import parse_glob_pattern


def strip_glob_prefix(glob_pattern: str, prefix_dir: str) -> str | None:
    """Strip a literal directory prefix from a glob pattern.

    Only removes the prefix if the pattern's leading literal segments
    match the prefix directory exactly. Returns None if the prefix
    doesn't match.

    Args:
        glob_pattern: Glob pattern string (e.g., "lore/globs/**/*.py")
        prefix_dir: Directory prefix to strip (e.g., "lore/globs")

    Returns:
        Pattern with prefix removed (e.g., "**/*.py"), or None if
        prefix doesn't match the pattern's literal segments.

    Examples:
        ("lore/globs/**/*.py", "lore/globs") -> "**/*.py"
        ("lore/globs/file.py", "lore") -> "globs/file.py"
        ("**/*.py", "lore") -> None  (no literal prefix to strip)
        ("src/**/*.py", "other") -> None  (prefix doesn't match)
    """
    if not prefix_dir or prefix_dir == ".":
        return glob_pattern

    prefix_segments = split_path_segments(prefix_dir)
    if not prefix_segments:
        return glob_pattern

    parsed = parse_glob_pattern(glob_pattern)
    segments = parsed["segments"]

    # Check that the pattern has enough literal segments to match prefix
    if len(segments) < len(prefix_segments):
        return None

    # Verify each prefix segment matches a literal segment in the pattern
    for i, prefix_seg in enumerate(prefix_segments):
        seg = segments[i]
        if seg["type"] != "literal" or seg["value"] != prefix_seg:
            return None

    # Build the remaining pattern from segments after the prefix
    remaining_segments = segments[len(prefix_segments):]

    if not remaining_segments:
        return None

    remaining_parts = [seg["value"] for seg in remaining_segments]
    result = join_path_segments(remaining_parts)

    # Preserve trailing slash if original had one
    if parsed["is_dir"]:
        result += "/"

    return result
