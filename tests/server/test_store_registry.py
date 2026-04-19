import json
import time

from lore.server.store_registry import get_or_build_store, evict_idle_stores


def test_get_or_build_store_creates_on_first_access(tmp_path):
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": {"fact": "Py", "incl": ["p:**/*.py"]}}))
    stores = {}
    store = get_or_build_store(stores, str(tmp_path))
    assert store.get_fact("f1") is not None
    assert str(tmp_path) in stores


def test_get_or_build_store_returns_same_instance(tmp_path):
    (tmp_path / ".lore.json").write_text(json.dumps({}))
    stores = {}
    store1 = get_or_build_store(stores, str(tmp_path))
    store2 = get_or_build_store(stores, str(tmp_path))
    assert store1 is store2


def test_get_or_build_store_separate_for_different_roots(tmp_path):
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    root_a.mkdir()
    root_b.mkdir()
    stores = {}
    store_a = get_or_build_store(stores, str(root_a))
    store_b = get_or_build_store(stores, str(root_b))
    assert store_a is not store_b
    assert len(stores) == 2


def test_evict_idle_stores_removes_old(tmp_path):
    (tmp_path / ".lore.json").write_text(json.dumps({}))
    stores = {}
    get_or_build_store(stores, str(tmp_path))
    # Backdate the entry
    stores[str(tmp_path)].last_access = time.monotonic() - 100
    evicted = evict_idle_stores(stores, evict_after=50)
    assert str(tmp_path) in evicted
    assert len(stores) == 0


def test_evict_idle_stores_keeps_recent(tmp_path):
    (tmp_path / ".lore.json").write_text(json.dumps({}))
    stores = {}
    get_or_build_store(stores, str(tmp_path))
    evicted = evict_idle_stores(stores, evict_after=9999)
    assert evicted == []
    assert len(stores) == 1
