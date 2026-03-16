import json
import pytest

from lore.store.load_facts_file import load_facts_file
from tests.test_helpers.build_test_fact import build_test_fact
from tests.test_helpers.build_test_fact_set import build_test_fact_set


def test_load_valid_rules_file(tmp_path):
    rules_file = tmp_path / ".lore.json"
    _, fact = build_test_fact(fact_id="1", incl=["g:**/api.js"])
    rules_file.write_text(json.dumps({"1": fact}))

    rules = load_facts_file(str(rules_file))
    assert "1" in rules
    assert rules["1"]["fact"] == "Test fact"
    assert rules["1"]["incl"] == ["g:**/api.js"]


def test_load_valid_with_skip(tmp_path):
    rules_file = tmp_path / ".lore.json"
    _, fact = build_test_fact(incl=["g:**/*.js"], skip=["g:vendor/**"])
    rules_file.write_text(json.dumps({"1": fact}))

    rules = load_facts_file(str(rules_file))
    assert rules["1"]["skip"] == ["g:vendor/**"]


def test_load_multiple_facts(tmp_path):
    rules_file = tmp_path / ".lore.json"
    ruleset = build_test_fact_set(
        build_test_fact(fact_id="f1", incl=["g:**/*.js"]),
        build_test_fact(fact_id="f2", incl=["g:**/*.ts"]),
    )
    rules_file.write_text(json.dumps(ruleset))

    rules = load_facts_file(str(rules_file))
    assert "f1" in rules
    assert "f2" in rules


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_facts_file("/nonexistent/.lore.json")


def test_load_invalid_json(tmp_path):
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text("not valid json")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_facts_file(str(rules_file))


def test_load_non_object_json(tmp_path):
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps(["a", "b"]))

    with pytest.raises(ValueError, match="must contain a JSON object"):
        load_facts_file(str(rules_file))


def test_load_non_object_fact(tmp_path):
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"1": "not a fact object"}))

    with pytest.raises(ValueError, match="must be an object"):
        load_facts_file(str(rules_file))


def test_load_preserves_fact_structure(tmp_path):
    rules_file = tmp_path / ".lore.json"
    content = {
        "uuid-123": {
            "fact": "Backend API endpoints must be authenticated.",
            "incl": ["g:**/backend/**", "g:**/api.js"],
            "skip": ["g:vendor/**", "g:**/*.min.js"],
        }
    }
    rules_file.write_text(json.dumps(content))

    rules = load_facts_file(str(rules_file))
    assert rules["uuid-123"]["fact"] == "Backend API endpoints must be authenticated."
    assert len(rules["uuid-123"]["incl"]) == 2
    assert len(rules["uuid-123"]["skip"]) == 2
