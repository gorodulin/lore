import os

from lore.resolve_platform_cache_dir import resolve_platform_cache_dir


def test_darwin_returns_library_caches(monkeypatch):
    monkeypatch.setattr("lore.resolve_platform_cache_dir.sys.platform", "darwin")
    expected = os.path.join(os.path.expanduser("~"), "Library", "Caches")
    assert resolve_platform_cache_dir() == expected


def test_linux_uses_xdg_cache_home(monkeypatch):
    monkeypatch.setattr("lore.resolve_platform_cache_dir.sys.platform", "linux")
    monkeypatch.setenv("XDG_CACHE_HOME", "/xdg")
    assert resolve_platform_cache_dir() == "/xdg"


def test_linux_defaults_to_dot_cache(monkeypatch):
    monkeypatch.setattr("lore.resolve_platform_cache_dir.sys.platform", "linux")
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    expected = os.path.join(os.path.expanduser("~"), ".cache")
    assert resolve_platform_cache_dir() == expected
