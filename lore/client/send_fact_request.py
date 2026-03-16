import asyncio
import uuid

from lore.server.protocol.encode_fact_request import encode_fact_request
from lore.server.protocol.decode_fact_response import decode_fact_response


def send_fact_request(socket_path: str, method: str, params: dict | None = None, timeout: float = 5.0, project_root: str | None = None) -> dict:
    """Send a single request to the lore server and return the result.

    Synchronous wrapper around an async Unix socket call.
    Raises ConnectionError, TimeoutError, or ValueError (on server error).
    """
    return asyncio.run(send_fact_request_async(socket_path, method, params, timeout, project_root))


async def send_fact_request_async(socket_path: str, method: str, params: dict | None, timeout: float, project_root: str | None = None) -> dict:
    """Async version of send_fact_request for use inside an existing event loop."""
    request_id = uuid.uuid4().hex[:8]

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_unix_connection(socket_path),
            timeout=timeout,
        )
    except (FileNotFoundError, ConnectionRefusedError) as e:
        raise ConnectionError(f"Cannot connect to lore server: {e}") from e
    except asyncio.TimeoutError:
        raise TimeoutError("Connection to lore server timed out")

    try:
        writer.write(encode_fact_request(request_id, method, params, project_root=project_root))
        await writer.drain()

        line = await asyncio.wait_for(reader.readline(), timeout=timeout)
        if not line:
            raise ConnectionError("Server closed connection without response")

        _, result, error = decode_fact_response(line)
        if error is not None:
            raise ValueError(f"Server error [{error.get('code', '?')}]: {error.get('message', '')}")
        return result or {}
    except asyncio.TimeoutError:
        raise TimeoutError("Waiting for lore server response timed out")
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionResetError, BrokenPipeError):
            pass
