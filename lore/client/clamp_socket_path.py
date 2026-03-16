import os
import sys
import tempfile


# macOS: 104, Linux: 108. Use the tighter limit as safe default.
_UNIX_SOCKET_PATH_LIMIT = 104 if sys.platform == "darwin" else 108


def clamp_socket_path(socket_path: str) -> str:
    """Return *socket_path* unchanged if it fits the OS limit, otherwise a short fallback.

    Unix domain sockets have a hard limit on sun_path length (104 on macOS,
    108 on Linux). Long paths (e.g. from Nix store) can exceed this. When
    that happens, fall back to /tmp/lore-<uid>/<basename>.
    """
    if len(socket_path.encode()) <= _UNIX_SOCKET_PATH_LIMIT:
        return socket_path
    basename = os.path.basename(socket_path)
    return os.path.join(tempfile.gettempdir(), f"lore-{os.getuid()}", basename)
