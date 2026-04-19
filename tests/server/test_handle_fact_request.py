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
    store = _make_store(tmp_path, {"f1": {"fact": "Py", "incl": ["p:**/*.py"]}})
    result = handle_fact_request(store, "find_facts", {"file_path": "src/app.py"})
    assert "f1" in result


def test_find_facts_missing_file_path(tmp_path):
    store = _make_store(tmp_path)
    with pytest.raises(ValueError, match="file_path"):
        handle_fact_request(store, "find_facts", {})


def test_find_facts_by_tools_only(tmp_path):
    store = _make_store(tmp_path, {
        "f1": {"fact": "Git push is risky", "incl": ["t:git push"]},
    })
    result = handle_fact_request(store, "find_facts", {"tools": ["git push"]})
    assert "f1" in result


def test_find_facts_tools_list_forwarded_as_tuple(tmp_path):
    """RPC receives tools as a JSON array; handler must pass it through per-item."""
    store = _make_store(tmp_path, {
        "f1": {"fact": "Kubectl apply", "incl": ["t:kubectl apply"]},
    })
    result = handle_fact_request(
        store, "find_facts", {"tools": ["echo", "kubectl apply"]}
    )
    assert "f1" in result


def test_find_facts_by_endpoints_only(tmp_path):
    store = _make_store(tmp_path, {
        "f1": {"fact": "Prod", "incl": ["e:\\.prod\\."]},
    })
    result = handle_fact_request(
        store, "find_facts", {"endpoints": ["api.prod.com"]}
    )
    assert "f1" in result


def test_find_facts_endpoints_list_forwarded_as_tuple(tmp_path):
    store = _make_store(tmp_path, {
        "f1": {"fact": "Prod", "incl": ["e:\\.prod\\."]},
    })
    result = handle_fact_request(
        store, "find_facts", {"endpoints": ["api.staging.com", "api.prod.com"]}
    )
    assert "f1" in result


def test_read_fact(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Py", "incl": ["p:**/*.py"]}})
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
        "incl": ["p:**/*.ts"],
    })
    assert "fact_id" in result
    assert result["fact"] == "New fact"


def test_edit_fact(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Old", "incl": ["p:**/*.py"]}})
    result = handle_fact_request(store, "edit_fact", {
        "fact_id": "f1",
        "fact": "New",
    })
    assert result["fact"] == "New"


def test_delete_fact(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Doomed", "incl": ["p:**/*.py"]}})
    result = handle_fact_request(store, "delete_fact", {"fact_id": "f1"})
    assert result["fact_id"] == "f1"
    assert store.get_fact("f1") is None


def test_validate(tmp_path):
    store = _make_store(tmp_path, {"f1": {"fact": "Valid", "incl": ["p:**/*.py"]}})
    result = handle_fact_request(store, "validate", {})
    assert result["valid"] is True


def test_unknown_method(tmp_path):
    store = _make_store(tmp_path)
    with pytest.raises(ValueError, match="Unknown method"):
        handle_fact_request(store, "bogus", {})
