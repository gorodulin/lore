from lore.client.try_send_fact_request import try_send_fact_request


def test_returns_none_when_no_server(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    result = try_send_fact_request(str(tmp_path), "ping", {})
    assert result is None


def test_returns_none_on_bad_socket_path(tmp_path, monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", str(tmp_path))
    result = try_send_fact_request(str(tmp_path), "find_facts", {"file_path": "x.py"})
    assert result is None
