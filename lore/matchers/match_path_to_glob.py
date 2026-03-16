from lore.paths.split_path_segments import split_path_segments
from lore.matchers.match_path_segments import match_path_segments


def match_path_to_glob(compiled: dict, path: str) -> bool:
    """Return True if the path matches the compiled glob pattern.

    Directory paths must have a trailing slash (e.g., "src/utils/").
    File paths must not have a trailing slash (e.g., "src/utils/file.ts").

    Args:
        compiled: Compiled pattern dict from compile_glob_pattern
        path: Normalized path string (trailing / indicates directory)

    Returns:
        True if path matches the pattern

    Examples:
        pattern "src/**/test.ts" matches "src/utils/test.ts"
        pattern "src/**/test.ts" matches "src/test.ts" (** matches 0 segments)
        pattern "*.js" matches "app.js"
        pattern "src/" matches "src/" but not "src"
    """
    is_dir = path.endswith("/")
    segments = split_path_segments(path)
    return match_path_segments(compiled, segments, is_dir=is_dir)
