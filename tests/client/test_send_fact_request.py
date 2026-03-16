import asyncio
import json
import os
import tempfile

import pytest

from lore.client.send_fact_request import send_fact_request, send_fact_request_async
from lore.server.serve_lore_socket import serve_lore_socket


def _run_with_server(tmp_path, coro_fn, facts=None):
    """Run a coroutine with a live server, then clean up."""
    if facts is not None:
        (tmp_path / ".lore.json").write_text(json.dumps(facts))
    socket_path = os.path.join(tempfile.mkdtemp(), "fp.sock")

    async def _run():
        task = asyncio.create_task(serve_lore_socket({}, socket_path))
        for _ in range(50):
            await asyncio.sleep(0.02)
            if os.path.exists(socket_path):
                break
        try:
            return await coro_fn(socket_path, str(tmp_path))
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    return asyncio.run(_run())


def test_ping_round_trip(tmp_path):
    async def _test_async(socket_path, project_root):
        return await send_fact_request_async(socket_path, "ping", None, 5.0)

    result = _run_with_server(tmp_path, _test_async)
    assert result == {"status": "ok"}


def test_server_error(tmp_path):
    async def _test_async(socket_path, project_root):
        return await send_fact_request_async(socket_path, "read_fact", {"fact_id": "nope"}, 5.0, project_root=project_root)

    with pytest.raises(ValueError, match="Server error"):
        _run_with_server(tmp_path, _test_async)


def test_connection_error():
    with pytest.raises(ConnectionError):
        send_fact_request("/tmp/nonexistent.sock", "ping")


def test_find_facts_round_trip(tmp_path):
    facts = {"f1": {"fact": "Python", "incl": ["g:**/*.py"]}}

    async def _test_async(socket_path, project_root):
        return await send_fact_request_async(socket_path, "find_facts", {"file_path": "src/app.py"}, 5.0, project_root=project_root)

    result = _run_with_server(tmp_path, _test_async, facts=facts)
    assert "f1" in result
