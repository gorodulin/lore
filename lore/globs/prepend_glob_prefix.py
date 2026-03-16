from lore.paths.normalize_path import normalize_path


def prepend_glob_prefix(glob_pattern: str, prefix_dir: str) -> str:
    """Rewrite a local-root pattern to be global-root by prefixing.

    Prepends the prefix directory to the pattern, handling the case
    where the pattern starts with ** specially.

    Args:
        glob_pattern: Local-root glob pattern
        prefix_dir: Directory path to prepend (without trailing slash)

    Returns:
        Global-root pattern with prefix prepended

    Examples:
        ("**/api.js", "app") -> "app/**/api.js"
        ("*.html", "app") -> "app/*.html"
        ("src/file.ts", "app") -> "app/src/file.ts"
    """
    # Normalize prefix (remove trailing slash)
    prefix_dir = normalize_path(prefix_dir, assume_dir=False)

    if not prefix_dir or prefix_dir == ".":
        return glob_pattern

    # Simply prepend the prefix with a slash
    return f"{prefix_dir}/{glob_pattern}"
