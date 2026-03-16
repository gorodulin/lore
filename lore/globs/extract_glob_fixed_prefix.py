def extract_glob_fixed_prefix(compiled: dict) -> list[str]:
    """Return literal directory segments before the first wildcard.

    This is useful for:
    - Index lookups (narrowing candidates by prefix)
    - Determining relocation safety

    Args:
        compiled: A compiled pattern dict from compile_glob_pattern

    Returns:
        List of literal segment strings before any wildcard or globstar.
        Returns empty list if pattern starts with a wildcard.

    Examples:
        "src/utils/file.ts" -> ["src", "utils", "file.ts"]
        "src/**/test.js" -> ["src"]
        "**/api.js" -> []
        "src/*/index.ts" -> ["src"]
    """
    return compiled.get("fixed_prefix", [])
