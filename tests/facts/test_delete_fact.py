import json
import pytest

from lore.facts.delete_fact import delete_fact
from lore.store.load_facts_file import load_facts_file
from tests.test_helpers.build_test_fact import build_test_fact


def test_delete_basic(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact}))

    result = delete_fact(str(tmp_path), "f1")

    assert result["fact_id"] == "f1"
    assert result["fact"] == "Test fact"
    # File should be deleted since ruleset is now empty
    assert not rules_file.exists()


def test_delete_preserves_other_facts(tmp_path):
    _, fact1 = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    _, fact2 = build_test_fact(fact_id="f2", incl=["p:**/*.js"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact1, "f2": fact2}))

    delete_fact(str(tmp_path), "f1")

    loaded = load_facts_file(str(rules_file))
    assert "f1" not in loaded
    assert "f2" in loaded


def test_delete_not_found(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact}))

    with pytest.raises(ValueError, match="not found"):
        delete_fact(str(tmp_path), "nonexistent")


def test_delete_empty_tree(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        delete_fact(str(tmp_path), "f1")


def test_delete_from_subdirectory(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    rules_file = sub_dir / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact}))

    result = delete_fact(str(tmp_path), "f1")

    assert result["fact_id"] == "f1"
    assert not rules_file.exists()


def test_delete_returns_deleted_fact(tmp_path):
    _, fact = build_test_fact(fact_id="f1", fact_text="Important fact", incl=["p:**/*.py"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact}))

    result = delete_fact(str(tmp_path), "f1")

    assert result["fact"] == "Important fact"
    assert result["incl"] == ["p:**/*.py"]
