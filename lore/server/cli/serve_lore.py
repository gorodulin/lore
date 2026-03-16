import asyncio

from lore.server.serve_lore_socket import serve_lore_socket
from lore.client.resolve_lore_socket_path import resolve_lore_socket_path


def serve_lore():
    """Entry point for the lore-server daemon."""
    socket_path = resolve_lore_socket_path()
    asyncio.run(serve_lore_socket({}, socket_path))


if __name__ == "__main__":
    serve_lore()
