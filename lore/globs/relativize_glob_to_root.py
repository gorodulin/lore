from lore.globs.compile_glob_pattern import compile_glob_pattern
from lore.globs.extract_glob_fixed_prefix import extract_glob_fixed_prefix
from lore.globs.strip_glob_prefix import strip_glob_prefix
from lore.paths.split_path_segments import split_path_segments


def relativize_glob_to_root(glob_pattern: str, new_root: str) -> str | None:
    """Safely relocate a glob pattern relative to a new root directory.

    Strips the new_root prefix from the pattern, but only if doing so
    doesn't change the pattern's match semantics. Returns None if the
    relocation is unsafe (e.g., prefix doesn't match literal segments).

    Args:
        glob_pattern: Global-scope glob pattern (e.g., "lore/globs/**/*.py")
        new_root: Target directory to relativize to (e.g., "lore/globs")

    Returns:
        Relativized pattern (e.g., "**/*.py"), or None if relocation
        would change match semantics.

    Examples:
        ("lore/globs/**/*.py", "lore/globs") -> "**/*.py"
        ("**/*.py", "lore") -> None  (globstar at start, unsafe)
        ("src/test.py", "other") -> None  (prefix mismatch)
    """
    if not new_root or new_root == ".":
        return glob_pattern

    compiled = compile_glob_pattern(glob_pattern)
    if not compiled["valid"]:
        return None

    fixed_prefix = extract_glob_fixed_prefix(compiled)

    # The pattern must have enough literal prefix to cover the new root
    # Otherwise removing the prefix could change match semantics
    root_segments = split_path_segments(new_root)

    if len(fixed_prefix) < len(root_segments):
        return None

    return strip_glob_prefix(glob_pattern, new_root)
