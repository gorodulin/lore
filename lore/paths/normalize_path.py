import unicodedata


def normalize_path(path: str, *, assume_dir: bool | None = None) -> str:
    """Normalize path to repo-canonical form (unicode-safe, '/' separators).

    Args:
        path: Input path (may use \\ or / separators)
        assume_dir: If True, ensure trailing slash. If False, remove trailing slash.
                    If None, preserve the original intent.

    Returns:
        Normalized path with:
        - Unicode NFC normalization
        - Forward slashes only
        - No leading ./
        - No double slashes
        - No trailing slash (unless assume_dir=True or originally present with assume_dir=None)
    """
    # Unicode NFC normalization for consistent comparison
    path = unicodedata.normalize("NFC", path)

    # Convert backslashes to forward slashes
    path = path.replace("\\", "/")

    # Track if original had trailing slash
    had_trailing_slash = path.endswith("/") and len(path) > 1

    # Remove leading ./
    while path.startswith("./"):
        path = path[2:]

    # Collapse double slashes
    while "//" in path:
        path = path.replace("//", "/")

    # Remove trailing slash for processing
    if path.endswith("/") and len(path) > 1:
        path = path[:-1]

    # Handle empty path
    if not path:
        path = "."

    # Apply trailing slash based on assume_dir
    if assume_dir is True:
        if path != "." and not path.endswith("/"):
            path = path + "/"
    elif assume_dir is None and had_trailing_slash:
        if path != "." and not path.endswith("/"):
            path = path + "/"

    return path
