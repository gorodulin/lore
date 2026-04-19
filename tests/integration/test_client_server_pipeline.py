"""Client + server pipeline integration tests.

Start a lore server in-process on a temp socket and exercise it through
the client's ``send_fact_request_async`` API. Covers the wire protocol
end-to-end for every method the server dispatches: ping, find_facts,
create_fact, read_fact, edit_fact, delete_fact, validate.

Complements ``tests/server/test_serve_lore_socket.py`` (which uses raw
encode/decode helpers) by going through the client layer as the
collector and MCP shim actually do in production.
"""

import asyncio
import json
import os
import tempfile

import pytest

from lore.client.send_fact_request import send_fact_request_async
from lore.server.serve_lore_socket import serve_lore_socket


async def _start_server(tmp_path, facts=None):
    if facts is not None:
        (tmp_path / ".lore.json").write_text(json.dumps(facts))
    # Unix sockets have a ~108 byte path limit; stick to /tmp.
    socket_path = os.path.join(tempfile.mkdtemp(), "lore.sock")
    task = asyncio.create_task(serve_lore_socket({}, socket_path))

    for _ in range(50):
        await asyncio.sleep(0.02)
        if os.path.exists(socket_path):
            break
    return task, socket_path


async def _stop_server(task):
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_ping_via_client(tmp_path):
    task, socket_path = await _start_server(tmp_path)
    try:
        result = await send_fact_request_async(socket_path, "ping", None, 5.0)
        assert result == {"status": "ok"}
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_find_facts_roundtrip(tmp_path):
    task, socket_path = await _start_server(tmp_path, facts={
        "py-fact": {"fact": "Python files", "incl": ["p:**/*.py"]},
        "ts-fact": {"fact": "TypeScript files", "incl": ["p:**/*.ts"]},
    })
    try:
        result = await send_fact_request_async(
            socket_path, "find_facts",
            {"file_path": "src/app.py"},
            5.0, project_root=str(tmp_path),
        )
        assert "py-fact" in result
        assert "ts-fact" not in result
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_create_then_find_roundtrip(tmp_path):
    task, socket_path = await _start_server(tmp_path, facts={})
    try:
        created = await send_fact_request_async(
            socket_path, "create_fact",
            {
                "fact": "Kotlin source rule",
                "incl": ["p:**/*.kt"],
                "tags": ["kind:convention"],
            },
            5.0, project_root=str(tmp_path),
        )
        fact_id = created["fact_id"]
        assert fact_id

        result = await send_fact_request_async(
            socket_path, "find_facts",
            {"file_path": "app/Main.kt"},
            5.0, project_root=str(tmp_path),
        )
        assert fact_id in result
        assert result[fact_id]["fact"] == "Kotlin source rule"
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_edit_then_find_reflects_update(tmp_path):
    task, socket_path = await _start_server(tmp_path, facts={
        "kt-fact": {"fact": "Original text", "incl": ["p:**/*.kt"]},
    })
    try:
        await send_fact_request_async(
            socket_path, "edit_fact",
            {"fact_id": "kt-fact", "fact": "Updated text"},
            5.0, project_root=str(tmp_path),
        )
        result = await send_fact_request_async(
            socket_path, "find_facts",
            {"file_path": "app/Main.kt"},
            5.0, project_root=str(tmp_path),
        )
        assert result["kt-fact"]["fact"] == "Updated text"
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_delete_then_find_excludes_fact(tmp_path):
    task, socket_path = await _start_server(tmp_path, facts={
        "kt-fact": {"fact": "Will be deleted", "incl": ["p:**/*.kt"]},
    })
    try:
        await send_fact_request_async(
            socket_path, "delete_fact",
            {"fact_id": "kt-fact"},
            5.0, project_root=str(tmp_path),
        )
        result = await send_fact_request_async(
            socket_path, "find_facts",
            {"file_path": "app/Main.kt"},
            5.0, project_root=str(tmp_path),
        )
        assert "kt-fact" not in result
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_read_fact_returns_shape(tmp_path):
    task, socket_path = await _start_server(tmp_path, facts={
        "kt-fact": {
            "fact": "Kotlin files should use sealed classes",
            "incl": ["p:**/*.kt"],
            "tags": ["kind:design"],
        },
    })
    try:
        result = await send_fact_request_async(
            socket_path, "read_fact",
            {"fact_id": "kt-fact"},
            5.0, project_root=str(tmp_path),
        )
        assert result["fact_id"] == "kt-fact"
        assert result["fact"] == "Kotlin files should use sealed classes"
        assert "p:**/*.kt" in result["incl"]
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_find_with_description_matches_d_fact(tmp_path):
    task, socket_path = await _start_server(tmp_path, facts={
        "deploy-rule": {
            "fact": "Deploy runs cost money",
            "incl": ["d:(?i)deploy"],
            "tags": ["hook:bash"],
        },
    })
    try:
        result = await send_fact_request_async(
            socket_path, "find_facts",
            {"description": "Deploy to prod"},
            5.0, project_root=str(tmp_path),
        )
        assert "deploy-rule" in result
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_find_rejects_request_without_any_event_field(tmp_path):
    """file_path and description/command all missing -> server rejects."""
    task, socket_path = await _start_server(tmp_path, facts={})
    try:
        with pytest.raises(ValueError, match="find_facts requires"):
            await send_fact_request_async(
                socket_path, "find_facts",
                {},
                5.0, project_root=str(tmp_path),
            )
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_find_with_tools_matches_t_fact(tmp_path):
    """tools param over the wire fires a t: fact per-item."""
    task, socket_path = await _start_server(tmp_path, facts={
        "git-push-rule": {
            "fact": "Force push requires review",
            "incl": ["t:git push"],
            "tags": ["hook:bash"],
        },
    })
    try:
        result = await send_fact_request_async(
            socket_path, "find_facts",
            {"tools": ["echo", "git push"]},
            5.0, project_root=str(tmp_path),
        )
        assert "git-push-rule" in result
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_find_with_endpoints_matches_e_fact(tmp_path):
    """endpoints param over the wire fires an e: fact per-item."""
    task, socket_path = await _start_server(tmp_path, facts={
        "prod-rule": {
            "fact": "Prod calls need incident window",
            "incl": ["e:\\.prod\\."],
            "tags": ["hook:bash"],
        },
    })
    try:
        result = await send_fact_request_async(
            socket_path, "find_facts",
            {"endpoints": ["api.staging.com", "api.prod.com"]},
            5.0, project_root=str(tmp_path),
        )
        assert "prod-rule" in result
    finally:
        await _stop_server(task)


@pytest.mark.asyncio
async def test_find_with_flags_matches_f_fact(tmp_path):
    """flags param over the wire fires an f: literal per-item."""
    task, socket_path = await _start_server(tmp_path, facts={
        "mut-rule": {
            "fact": "Mutating commands require review",
            "incl": ["f:mutates"],
            "tags": ["hook:bash"],
        },
    })
    try:
        result = await send_fact_request_async(
            socket_path, "find_facts",
            {"flags": ["network", "mutates"]},
            5.0, project_root=str(tmp_path),
        )
        assert "mut-rule" in result
    finally:
        await _stop_server(task)
