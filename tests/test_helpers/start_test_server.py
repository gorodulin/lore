import asyncio

from lore.server.serve_lore_socket import serve_lore_socket


async def start_test_server(root: str, socket_path: str) -> tuple[asyncio.Task, dict]:
    """Start a lore socket server as a background asyncio task.

    Returns (server_task, stores_dict). Cancel server_task to shut down.
    The stores dict is empty; stores are created lazily on first request.
    """
    stores = {}
    task = asyncio.create_task(serve_lore_socket(stores, socket_path))

    # Wait briefly for socket to be ready
    for _ in range(50):
        await asyncio.sleep(0.02)
        try:
            r, w = await asyncio.open_unix_connection(socket_path)
            w.close()
            await w.wait_closed()
            break
        except (FileNotFoundError, ConnectionRefusedError):
            continue

    return task, stores
