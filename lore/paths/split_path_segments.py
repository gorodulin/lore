def split_path_segments(path: str) -> list[str]:
    """Split a normalized path into non-empty segments.

    Args:
        path: A normalized path string

    Returns:
        List of path segments (directory/file names).
        Empty list for "." or empty path.

    Examples:
        "src/utils/file.ts" -> ["src", "utils", "file.ts"]
        "src/" -> ["src"]
        "." -> []
        "" -> []
    """
    # Handle empty or root path
    if not path or path == ".":
        return []

    # Remove trailing slash if present
    if path.endswith("/"):
        path = path[:-1]

    # Split and filter empty segments
    return [seg for seg in path.split("/") if seg]
