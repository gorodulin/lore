import os

from lore.client.clamp_socket_path import clamp_socket_path
from lore.resolve_cache_dir import resolve_cache_dir


def resolve_lore_socket_path() -> str:
    """Return the global lore socket path.

    Builds the path from resolve_cache_dir() and clamps it to the
    OS socket path length limit, falling back to a short /tmp path.
    """
    return clamp_socket_path(os.path.join(resolve_cache_dir(), "lore.sock"))
