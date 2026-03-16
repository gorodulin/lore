def join_path_segments(segments: list[str], *, trailing_slash: bool = False) -> str:
    """Join path segments into a normalized path string.

    Args:
        segments: List of path segment strings
        trailing_slash: If True, append trailing slash to result

    Returns:
        Joined path string. Returns "." for empty segments list.

    Examples:
        (["src", "utils"], trailing_slash=False) -> "src/utils"
        (["src", "utils"], trailing_slash=True) -> "src/utils/"
        ([], trailing_slash=False) -> "."
    """
    if not segments:
        return "."

    result = "/".join(segments)

    if trailing_slash and not result.endswith("/"):
        result += "/"

    return result
