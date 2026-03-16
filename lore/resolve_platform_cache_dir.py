import os
import sys


def resolve_platform_cache_dir() -> str:
    """Return the platform-conventional user cache directory.

    macOS:  ~/Library/Caches
    Linux:  $XDG_CACHE_HOME or ~/.cache
    """
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Caches")
    xdg = os.environ.get("XDG_CACHE_HOME", "")
    if xdg:
        return xdg
    return os.path.join(os.path.expanduser("~"), ".cache")
