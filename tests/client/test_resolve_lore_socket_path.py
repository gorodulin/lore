from lore.client.resolve_lore_socket_path import resolve_lore_socket_path


def test_builds_socket_path_from_cache_dir(monkeypatch):
    monkeypatch.setattr(
        "lore.client.resolve_lore_socket_path.resolve_cache_dir",
        lambda: "/short/cache",
    )
    assert resolve_lore_socket_path() == "/short/cache/lore.sock"


def test_env_override(monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", "/tmp/fp-cache")
    result = resolve_lore_socket_path()
    assert result == "/tmp/fp-cache/lore.sock"


def test_clamps_long_path(monkeypatch):
    monkeypatch.setattr(
        "lore.client.resolve_lore_socket_path.resolve_cache_dir",
        lambda: "/nix/store/" + "a" * 100 + "/cache/lore",
    )
    result = resolve_lore_socket_path()
    assert "lore.sock" in result
    assert len(result.encode()) <= 108
