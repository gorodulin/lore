from unittest.mock import patch

from lore.client.try_send_fact_request import try_send_fact_request

# NOTE: Both functions must be patched on the try_send_fact_request module
# (where they're imported), not on their defining modules. This prevents
# ensure_lore_server from auto-starting a real lore server — which happens
# when lore hooks are active in the project itself.


def test_returns_none_when_server_unreachable(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    with patch(
        "lore.client.try_send_fact_request.is_lore_server_running", return_value=False
    ), patch(
        "lore.client.try_send_fact_request.ensure_lore_server", return_value=False
    ):
        result = try_send_fact_request(str(tmp_path), "ping", {})
    assert result is None


def test_returns_none_when_send_fails(tmp_path, monkeypatch):
    """Server is reachable but the request itself fails."""
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    with patch(
        "lore.client.try_send_fact_request.send_fact_request",
        side_effect=ConnectionRefusedError,
    ):
        result = try_send_fact_request(str(tmp_path), "find_facts", {"file_path": "x.py"})
    assert result is None
