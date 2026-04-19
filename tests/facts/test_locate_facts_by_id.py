import json

from lore.facts.locate_facts_by_id import locate_facts_by_id
from tests.test_helpers.build_test_fact import build_test_fact


def test_find_single_id(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": fact}))

    result = locate_facts_by_id(str(tmp_path), {"f1"})
    assert "f1" in result
    assert result["f1"]["fact"]["fact"] == "Test fact"


def test_find_multiple_ids_single_file(tmp_path):
    _, f1 = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    _, f2 = build_test_fact(fact_id="f2", incl=["p:**/*.js"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": f1, "f2": f2}))

    result = locate_facts_by_id(str(tmp_path), {"f1", "f2"})
    assert len(result) == 2
    assert "f1" in result
    assert "f2" in result


def test_find_multiple_ids_across_files(tmp_path):
    _, f1 = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": f1}))

    sub = tmp_path / "sub"
    sub.mkdir()
    _, f2 = build_test_fact(fact_id="f2", incl=["p:**/*.js"])
    (sub / ".lore.json").write_text(json.dumps({"f2": f2}))

    result = locate_facts_by_id(str(tmp_path), {"f1", "f2"})
    assert len(result) == 2
    assert result["f1"]["rel_dir"] == ""
    assert result["f2"]["rel_dir"] == "sub"


def test_partial_found(tmp_path):
    _, f1 = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": f1}))

    result = locate_facts_by_id(str(tmp_path), {"f1", "missing"})
    assert "f1" in result
    assert "missing" not in result
    assert len(result) == 1


def test_none_found(tmp_path):
    _, f1 = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": f1}))

    result = locate_facts_by_id(str(tmp_path), {"nonexistent"})
    assert result == {}


def test_empty_tree(tmp_path):
    result = locate_facts_by_id(str(tmp_path), {"f1"})
    assert result == {}


def test_empty_ids(tmp_path):
    _, f1 = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": f1}))

    result = locate_facts_by_id(str(tmp_path), set())
    assert result == {}


def test_result_includes_file_path(tmp_path):
    _, fact = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": fact}))

    result = locate_facts_by_id(str(tmp_path), {"f1"})
    assert result["f1"]["file_path"] == str(tmp_path / ".lore.json")


def test_early_exit_all_found(tmp_path):
    """When all IDs are found, remaining files are not scanned."""
    _, f1 = build_test_fact(fact_id="f1", incl=["p:**/*.py"])
    (tmp_path / ".lore.json").write_text(json.dumps({"f1": f1}))

    # Create a second file that won't be reached
    sub = tmp_path / "sub"
    sub.mkdir()
    _, f2 = build_test_fact(fact_id="f2", incl=["p:**/*.js"])
    (sub / ".lore.json").write_text(json.dumps({"f2": f2}))

    # Only searching for f1 - should find it in first file and stop
    result = locate_facts_by_id(str(tmp_path), {"f1"})
    assert len(result) == 1
    assert "f1" in result
