import os

from lore.resolve_platform_cache_dir import resolve_platform_cache_dir


def resolve_cache_dir() -> str:
    """Return the lore cache directory.

    Resolution order:
      LORE_CACHE_DIR > <platform cache>/lore

    Platform cache is ~/Library/Caches on macOS,
    $XDG_CACHE_HOME (or ~/.cache) on Linux.
    """
    cache_dir = os.environ.get("LORE_CACHE_DIR", "")
    if cache_dir:
        return cache_dir
    return os.path.join(resolve_platform_cache_dir(), "lore")
