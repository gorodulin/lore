import asyncio
import os
import signal
import time

from lore.server.protocol.decode_fact_request import decode_fact_request
from lore.server.protocol.encode_fact_response import encode_fact_response
from lore.server.handle_fact_request import handle_fact_request
from lore.server.store_registry import StoreEntry, get_or_build_store, evict_idle_stores


async def serve_lore_socket(stores: dict[str, StoreEntry], socket_path: str, idle_shutdown_seconds: float = 7200.0, evict_after: float = 1800.0, evict_interval: float = 60.0) -> None:
    """Run an asyncio Unix socket server for fact requests.

    Manages multiple project roots via the stores dict. Shuts down
    after idle_shutdown_seconds with no requests. Periodically evicts
    per-project stores unused for evict_after seconds.

    Cleans up socket and PID file on shutdown.
    """
    os.makedirs(os.path.dirname(socket_path), exist_ok=True)

    if os.path.exists(socket_path):
        os.remove(socket_path)

    pid_path = _pid_path_for_socket(socket_path)
    _write_pid_file(pid_path)

    last_request = [time.monotonic()]

    server = await asyncio.start_unix_server(
        lambda r, w: _handle_fact_connection(stores, r, w, last_request),
        path=socket_path,
    )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    idle_task = asyncio.create_task(
        _idle_shutdown_loop(stop_event, last_request, idle_shutdown_seconds, stores, evict_after, evict_interval),
    )

    try:
        async with server:
            await stop_event.wait()
    finally:
        idle_task.cancel()
        try:
            await idle_task
        except asyncio.CancelledError:
            pass
        server.close()
        await server.wait_closed()
        _remove_pid_file(pid_path)
        if os.path.exists(socket_path):
            os.remove(socket_path)


async def _handle_fact_connection(stores: dict[str, StoreEntry], reader: asyncio.StreamReader, writer: asyncio.StreamWriter, last_request: list[float]) -> None:
    """Handle a single client connection: read requests, write responses."""
    try:
        while True:
            line = await reader.readline()
            if not line:
                break

            last_request[0] = time.monotonic()

            try:
                request_id, method, params, project_root = decode_fact_request(line)
            except ValueError as e:
                resp = encode_fact_response("unknown", error={"code": "parse_error", "message": str(e)})
                writer.write(resp)
                await writer.drain()
                continue

            try:
                if not project_root and method != "ping":
                    raise ValueError("Request requires 'project_root'")
                store = get_or_build_store(stores, project_root) if project_root else None
                result = handle_fact_request(store, method, params)
                resp = encode_fact_response(request_id, result=result)
            except ValueError as e:
                resp = encode_fact_response(request_id, error={"code": "request_error", "message": str(e)})

            writer.write(resp)
            await writer.drain()
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionResetError, BrokenPipeError):
            pass


async def _idle_shutdown_loop(stop_event: asyncio.Event, last_request: list[float], idle_shutdown_seconds: float, stores: dict[str, StoreEntry], evict_after: float, interval: float = 60.0) -> None:
    """Periodically evict idle stores and shut down server if fully idle."""
    while not stop_event.is_set():
        await asyncio.sleep(interval)
        evict_idle_stores(stores, evict_after)
        if time.monotonic() - last_request[0] >= idle_shutdown_seconds:
            stop_event.set()
            return


def _pid_path_for_socket(socket_path: str) -> str:
    """Derive the PID file path from the socket path."""
    return socket_path.rsplit(".", 1)[0] + ".pid"


def _write_pid_file(pid_path: str) -> None:
    """Write current process PID to file."""
    with open(pid_path, "w") as f:
        f.write(str(os.getpid()))


def _remove_pid_file(pid_path: str) -> None:
    """Remove PID file if it exists."""
    try:
        os.remove(pid_path)
    except FileNotFoundError:
        pass
