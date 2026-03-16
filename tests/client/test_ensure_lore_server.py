import asyncio
import json
import os
import tempfile

from lore.client.ensure_lore_server import ensure_lore_server
from lore.server.serve_lore_socket import serve_lore_socket


def test_returns_true_when_already_running(tmp_path):
    (tmp_path / ".lore.json").write_text(json.dumps({}))
    socket_path = os.path.join(tempfile.mkdtemp(), "fp.sock")

    async def _run():
        task = asyncio.create_task(serve_lore_socket({}, socket_path))
        for _ in range(50):
            await asyncio.sleep(0.02)
            if os.path.exists(socket_path):
                break
        try:
            assert ensure_lore_server(socket_path) is True
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    asyncio.run(_run())
