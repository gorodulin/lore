import json

import pytest

from lore.factstore.fact_store import FactStore
from lore.server.handle_fact_request import handle_fact_request


def _make_store(tmp_path, facts=None):
    if facts is not None:
        (tmp_path / ".lore.json").write_text(json.dumps(facts))
    store = FactStore(str(tmp_path))
    store.load_all_facts()
    return store


def test_ping(tmp_path):
    store = _make_store(tmp_path)
    result = handle_fact_request(store, "ping", {})
    assert result == {"status": "ok"}


def test_find_facts(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Py", "incl": ["g:**/*.py"]}})
    result = handle_fact_request(store, "find_facts", {"file_path": "src/app.py"})
    assert "f1" in result


def test_find_facts_missing_file_path(tmp_path):
    store = _make_store(tmp_path)
    with pytest.raises(ValueError, match="file_path"):
        handle_fact_request(store, "find_facts", {})


def test_read_fact(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Py", "incl": ["g:**/*.py"]}})
    result = handle_fact_request(store, "read_fact", {"fact_id": "f1"})
    assert result["fact_id"] == "f1"
    assert result["fact"] == "Py"


def test_read_fact_not_found(tmp_path):
    store = _make_store(tmp_path)
    with pytest.raises(ValueError, match="not found"):
        handle_fact_request(store, "read_fact", {"fact_id": "missing"})


def test_create_fact(tmp_path):
    store = _make_store(tmp_path)
    result = handle_fact_request(store, "create_fact", {
        "fact": "New fact",
        "incl": ["g:**/*.ts"],
    })
    assert "fact_id" in result
    assert result["fact"] == "New fact"


def test_edit_fact(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Old", "incl": ["g:**/*.py"]}})
    result = handle_fact_request(store, "edit_fact", {
        "fact_id": "f1",
        "fact": "New",
    })
    assert result["fact"] == "New"


def test_delete_fact(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Doomed", "incl": ["g:**/*.py"]}})
    result = handle_fact_request(store, "delete_fact", {"fact_id": "f1"})
    assert result["fact_id"] == "f1"
    assert store.get_fact("f1") is None


def test_validate(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Valid", "incl": ["g:**/*.py"]}})
    result = handle_fact_request(store, "validate", {})
    assert result["valid"] is True


def test_unknown_method(tmp_path):
    store = _make_store(tmp_path)
    with pytest.raises(ValueError, match="Unknown method"):
        handle_fact_request(store, "bogus", {})
