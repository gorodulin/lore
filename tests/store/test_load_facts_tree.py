import json

from lore.store.load_facts_tree import load_facts_tree
from tests.test_helpers.build_test_fact import build_test_fact


def test_load_single_rules_file(tmp_path):
    _, fact = build_test_fact(incl=["p:*.ts"])
    rules_file = tmp_path / ".lore.json"
    rules_file.write_text(json.dumps({"1": fact}))

    results = load_facts_tree(str(tmp_path))
    assert len(results) == 1
    assert results[0]["rel_dir"] == ""
    assert "1" in results[0]["facts"]
    assert results[0]["facts"]["1"]["incl"] == ["p:*.ts"]


def test_load_nested_rules_files(tmp_path):
    # Root rules
    _, fact1 = build_test_fact(incl=["p:*.ts"])
    (tmp_path / ".lore.json").write_text(json.dumps({"1": fact1}))

    # Nested rules
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    _, fact2 = build_test_fact(incl=["p:**/api.js"])
    (app_dir / ".lore.json").write_text(json.dumps({"2": fact2}))

    results = load_facts_tree(str(tmp_path))
    assert len(results) == 2

    # Find by rel_dir
    root_rules = next(r for r in results if r["rel_dir"] == "")
    app_rules = next(r for r in results if r["rel_dir"] == "app")

    assert root_rules["facts"]["1"]["incl"] == ["p:*.ts"]
    assert app_rules["facts"]["2"]["incl"] == ["p:**/api.js"]


def test_load_deeply_nested(tmp_path):
    deep_dir = tmp_path / "a" / "b" / "c"
    deep_dir.mkdir(parents=True)
    _, fact = build_test_fact(incl=["p:*.js"])
    (deep_dir / ".lore.json").write_text(json.dumps({"1": fact}))

    results = load_facts_tree(str(tmp_path))
    assert len(results) == 1
    assert results[0]["rel_dir"] == "a/b/c"


def test_load_no_rules_files(tmp_path):
    results = load_facts_tree(str(tmp_path))
    assert results == []


def test_load_custom_filename(tmp_path):
    _, fact = build_test_fact(incl=["p:*.ts"])
    (tmp_path / "patterns.json").write_text(json.dumps({"1": fact}))

    results = load_facts_tree(str(tmp_path), filename="patterns.json")
    assert len(results) == 1
    assert results[0]["facts"]["1"]["incl"] == ["p:*.ts"]
