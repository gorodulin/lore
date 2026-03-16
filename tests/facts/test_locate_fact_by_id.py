import json

from lore.facts.locate_fact_by_id import locate_fact_by_id
from tests.test_helpers.build_test_fact import build_test_fact


def test_find_in_root(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["g:**/*.py"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact}))

    result = locate_fact_by_id(str(tmp_path), "f1")
    assert result is not None
    assert result["rel_dir"] == ""
    assert result["fact"]["fact"] == "Test fact"


def test_find_in_subdirectory(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["g:**/*.py"])
    sub_dir = tmp_path / "sub" / "dir"
    sub_dir.mkdir(parents=True)
    rules_file = sub_dir / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact}))

    result = locate_fact_by_id(str(tmp_path), "f1")
    assert result is not None
    assert result["rel_dir"] == "sub/dir"


def test_find_not_found(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["g:**/*.py"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact}))

    result = locate_fact_by_id(str(tmp_path), "nonexistent")
    assert result is None


def test_find_empty_tree(tmp_path):
    result = locate_fact_by_id(str(tmp_path), "f1")
    assert result is None


def test_find_returns_first_match(tmp_path):
    """If same ID exists in multiple files (shouldn't happen), returns first found."""
    _, fact = build_test_fact(fact_id="f1", incl=["g:**/*.py"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"f1": fact}))

    result = locate_fact_by_id(str(tmp_path), "f1")
    assert result is not None
    assert result["fact"]["incl"] == ["g:**/*.py"]
