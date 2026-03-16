import asyncio
import json
import os
import tempfile

from lore.client.is_lore_server_running import is_lore_server_running
from lore.factstore.build_fact_store import build_fact_store
from lore.server.serve_lore_socket import serve_lore_socket


def test_detects_already_running(tmp_path):
    (tmp_path / ".lore.json").write_text(json.dumps({}))
    store = build_fact_store(str(tmp_path))
    socket_path = os.path.join(tempfile.mkdtemp(), "fp.sock")

    async def _run():
        task = asyncio.create_task(serve_lore_socket(store, socket_path))
        for _ in range(50):
            await asyncio.sleep(0.02)
            if os.path.exists(socket_path):
                break
        try:
            assert is_lore_server_running(socket_path) is True
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    asyncio.run(_run())


def test_detects_no_server():
    assert is_lore_server_running("/tmp/nonexistent.sock") is False


def test_stale_socket_file(tmp_path):
    stale = tmp_path / "stale.sock"
    stale.write_text("not a real socket")
    assert is_lore_server_running(str(stale)) is False
