import json

import pytest
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.exceptions import ToolError

from lore.mcp.register_mcp_tools import register_mcp_tools


@pytest.fixture
async def mcp_client(tmp_path):
    mcp = FastMCP("lore-test")
    register_mcp_tools(mcp, str(tmp_path))
    async with Client(transport=mcp) as client:
        yield client


async def test_create_and_read_round_trip(mcp_client, tmp_path):
    result = await mcp_client.call_tool(
        "create_fact",
        {"fact": "Test fact", "incl": ["p:**/*.py"]},
    )
    created = _parse_data(result)
    fact_id = created["fact_id"]

    read_result = await mcp_client.call_tool(
        "read_fact",
        {"fact_id": fact_id},
    )
    read = _parse_data(read_result)
    assert read["fact_id"] == fact_id
    assert read["fact"] == "Test fact"
    assert read["incl"] == ["p:**/*.py"]


async def test_read_fact_globalizes_patterns(mcp_client, tmp_path):
    result = await mcp_client.call_tool(
        "create_fact",
        {"fact": "Subdir fact", "incl": ["p:sub/**/*.py"]},
    )
    fact_id = _parse_data(result)["fact_id"]

    read_result = await mcp_client.call_tool(
        "read_fact",
        {"fact_id": fact_id},
    )
    read = _parse_data(read_result)
    assert read["incl"] == ["p:sub/**/*.py"]


async def test_find_facts_matching(mcp_client, tmp_path):
    await mcp_client.call_tool(
        "create_fact",
        {"fact": "Python fact", "incl": ["p:**/*.py"]},
    )
    result = await mcp_client.call_tool(
        "find_facts",
        {"file_path": "src/main.py"},
    )
    found = _parse_data(result)
    assert len(found) == 1
    fact = next(iter(found.values()))
    assert fact["fact"] == "Python fact"


async def test_edit_updates_fact(mcp_client, tmp_path):
    result = await mcp_client.call_tool(
        "create_fact",
        {"fact": "Original", "incl": ["p:**/*.py"]},
    )
    fact_id = _parse_data(result)["fact_id"]

    await mcp_client.call_tool(
        "edit_fact",
        {"fact_id": fact_id, "fact": "Updated"},
    )

    read_result = await mcp_client.call_tool(
        "read_fact",
        {"fact_id": fact_id},
    )
    read = _parse_data(read_result)
    assert read["fact"] == "Updated"


async def test_delete_removes_fact(mcp_client, tmp_path):
    result = await mcp_client.call_tool(
        "create_fact",
        {"fact": "To delete", "incl": ["p:**/*.py"]},
    )
    fact_id = _parse_data(result)["fact_id"]

    delete_result = await mcp_client.call_tool(
        "delete_fact",
        {"fact_id": fact_id},
    )
    deleted = _parse_data(delete_result)
    assert deleted["fact_id"] == fact_id

    with pytest.raises(ToolError, match="not found"):
        await mcp_client.call_tool(
            "read_fact",
            {"fact_id": fact_id},
        )


async def test_read_missing_id_raises_error(mcp_client):
    with pytest.raises(ToolError, match="not found"):
        await mcp_client.call_tool(
            "read_fact",
            {"fact_id": "nonexistent"},
        )


async def test_create_invalid_pattern_raises_error(mcp_client):
    with pytest.raises(ToolError, match="Invalid fact"):
        await mcp_client.call_tool(
            "create_fact",
            {"fact": "Bad", "incl": ["no_prefix_pattern"]},
        )


def _parse_data(result):
    """Extract data from a CallToolResult, handling both .data and text content."""
    if hasattr(result, "data") and result.data is not None:
        data = result.data
        if isinstance(data, str):
            return json.loads(data)
        return data
    text = result.content[0].text
    return json.loads(text)
