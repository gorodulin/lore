import asyncio
import json
import os
import tempfile

import pytest

from lore.server.protocol.encode_fact_request import encode_fact_request
from lore.server.protocol.decode_fact_response import decode_fact_response
from lore.server.serve_lore_socket import serve_lore_socket


async def _start_server(tmp_path, facts=None, **kwargs):
    root = str(tmp_path)
    if facts is not None:
        (tmp_path / ".lore.json").write_text(json.dumps(facts))
    # Use a short /tmp path to avoid AF_UNIX path length limit
    socket_path = os.path.join(tempfile.mkdtemp(), "fp.sock")
    task = asyncio.create_task(serve_lore_socket({}, socket_path, **kwargs))

    for _ in range(50):
        await asyncio.sleep(0.02)
        if os.path.exists(socket_path):
            break

    return task, socket_path, root


async def _send_request(socket_path, method, params=None, project_root=None):
    reader, writer = await asyncio.open_unix_connection(socket_path)
    writer.write(encode_fact_request("t1", method, params, project_root=project_root))
    await writer.drain()
    line = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return decode_fact_response(line)


@pytest.mark.asyncio
async def test_ping_round_trip(tmp_path):
    task, socket_path, root = await _start_server(tmp_path)
    try:
        req_id, result, error = await _send_request(socket_path, "ping")
        assert req_id == "t1"
        assert result == {"status": "ok"}
        assert error is None
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_find_facts_round_trip(tmp_path):
    facts = {"f1": {"fact": "Python", "incl": ["g:**/*.py"]}}
    task, socket_path, root = await _start_server(tmp_path, facts)
    try:
        req_id, result, error = await _send_request(
            socket_path, "find_facts", {"file_path": "src/app.py"}, project_root=root,
        )
        assert error is None
        assert "f1" in result
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_handles_malformed_request(tmp_path):
    task, socket_path, root = await _start_server(tmp_path)
    try:
        reader, writer = await asyncio.open_unix_connection(socket_path)
        writer.write(b"not valid json\n")
        await writer.drain()
        line = await reader.readline()
        writer.close()
        await writer.wait_closed()

        req_id, result, error = decode_fact_response(line)
        assert error is not None
        assert error["code"] == "parse_error"
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_removes_socket_on_shutdown(tmp_path):
    task, socket_path, root = await _start_server(tmp_path)
    assert os.path.exists(socket_path)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    await asyncio.sleep(0.05)
    assert not os.path.exists(socket_path)


@pytest.mark.asyncio
async def test_rejects_request_without_project_root(tmp_path):
    task, socket_path, root = await _start_server(tmp_path)
    try:
        _, _, error = await _send_request(socket_path, "find_facts", {"file_path": "x.py"})
        assert error is not None
        assert "project_root" in error["message"]
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_multi_project_round_trip(tmp_path):
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    root_a.mkdir()
    root_b.mkdir()
    (root_a / ".lore.json").write_text(json.dumps({"fa": {"fact": "From A", "incl": ["g:**/*.py"]}}))
    (root_b / ".lore.json").write_text(json.dumps({"fb": {"fact": "From B", "incl": ["g:**/*.py"]}}))

    socket_path = os.path.join(tempfile.mkdtemp(), "fp.sock")
    task = asyncio.create_task(serve_lore_socket({}, socket_path))
    for _ in range(50):
        await asyncio.sleep(0.02)
        if os.path.exists(socket_path):
            break

    try:
        _, result_a, error_a = await _send_request(
            socket_path, "find_facts", {"file_path": "x.py"}, project_root=str(root_a),
        )
        assert error_a is None
        assert "fa" in result_a
        assert "fb" not in result_a

        _, result_b, error_b = await _send_request(
            socket_path, "find_facts", {"file_path": "x.py"}, project_root=str(root_b),
        )
        assert error_b is None
        assert "fb" in result_b
        assert "fa" not in result_b
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_idle_shutdown(tmp_path):
    task, socket_path, root = await _start_server(
        tmp_path, idle_shutdown_seconds=0.1, evict_after=0.05, evict_interval=0.05,
    )
    assert os.path.exists(socket_path)

    # Server should shut itself down after idle timeout
    await asyncio.wait_for(task, timeout=2.0)

    await asyncio.sleep(0.05)
    assert not os.path.exists(socket_path)
