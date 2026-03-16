import os
import tempfile

from lore.client.clamp_socket_path import clamp_socket_path


def test_short_path_unchanged():
    path = "/tmp/lore/lore.sock"
    assert clamp_socket_path(path) == path


def test_long_path_falls_back_to_tmp(monkeypatch):
    monkeypatch.setattr("lore.client.clamp_socket_path._UNIX_SOCKET_PATH_LIMIT", 30)
    long_path = "/nix/store/aaaaaaaaaaaaaaaaaaaaaaaaa/cache/lore/lore.sock"
    result = clamp_socket_path(long_path)
    expected = os.path.join(tempfile.gettempdir(), f"lore-{os.getuid()}", "lore.sock")
    assert result == expected


def test_exactly_at_limit_unchanged(monkeypatch):
    path = "/tmp/lore.sock"
    monkeypatch.setattr(
        "lore.client.clamp_socket_path._UNIX_SOCKET_PATH_LIMIT",
        len(path.encode()),
    )
    assert clamp_socket_path(path) == path
