from lore.resolve_cache_dir import resolve_cache_dir


def test_lore_cache_dir_takes_priority(monkeypatch):
    monkeypatch.setenv("LORE_CACHE_DIR", "/custom/cache")
    assert resolve_cache_dir() == "/custom/cache"


def test_delegates_to_platform_cache_dir(monkeypatch):
    monkeypatch.delenv("LORE_CACHE_DIR", raising=False)
    monkeypatch.setattr(
        "lore.resolve_cache_dir.resolve_platform_cache_dir",
        lambda: "/platform/cache",
    )
    assert resolve_cache_dir() == "/platform/cache/lore"
